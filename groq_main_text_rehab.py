
import json
import os
import re
import time
from groq import Groq

# --- CONFIGURATION ---
MODEL_ID = "llama-3.1-8b-instant"
INPUT_FILE = "main_text_repair_list.json"
OUTPUT_FILE = "checkpoint_main_text_groq.json"   # Write repairs directly back in
DELAY_SECONDS = 5
MAX_BATCH_WORDS = 300  # Main text is denser than footnotes — tighter packing

def load_env():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
client = Groq(api_key=os.environ.get("VITE_GROQ_API_KEY"))

SYSTEM_PROMPT_SINGLE = """You are an elite scholarly translator rendering Salomon Munk's 19th-century French into Victorian scholarly English.
CONSTRAINTS:
1. Preserve ALL [[t:N]] and [[fn:N]] markers exactly as they appear — do not alter, move, or remove them.
2. Preserve ALL Hebrew, Arabic, and Greek script exactly.
3. Translate Latin inline as [Lat.: ...].
4. Use formal Victorian scholarly prose: prefer 'one' over 'we', 'doubtless' over 'likely', passive constructions where appropriate.
5. Output the translated text ONLY. No preamble."""

SYSTEM_PROMPT_BATCH = """You are an elite scholarly translator rendering Salomon Munk's 19th-century French into Victorian scholarly English.
Translate each segment. CONSTRAINTS:
1. Preserve ALL [[t:N]] and [[fn:N]] markers exactly.
2. Preserve ALL Hebrew, Arabic, and Greek script exactly.
3. Translate Latin inline as [Lat.: ...].
4. Use formal Victorian scholarly prose.
5. Output JSON ONLY: {"results": [{"id": "...", "text": "..."}]}"""

def get_word_count(text):
    return len(re.findall(r'\w+', text))

def build_smart_batches(items):
    """Pack short segments together, send long ones alone."""
    batches = []
    current_batch = []
    current_words = 0

    # Sort ascending by word count so short ones cluster
    items_sorted = sorted(items, key=lambda x: get_word_count(x["fr_text"]))

    for item in items_sorted:
        wc = get_word_count(item["fr_text"])

        if wc > 250:  # Long segments always go alone
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_words = 0
            batches.append([item])
            continue

        if current_words + wc <= MAX_BATCH_WORDS and len(current_batch) < 4:
            current_batch.append(item)
            current_words += wc
        else:
            if current_batch:
                batches.append(current_batch)
            current_batch = [item]
            current_words = wc

    if current_batch:
        batches.append(current_batch)

    return batches

def translate_single(item):
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SINGLE},
                {"role": "user", "content": item["fr_text"]}
            ],
            model=MODEL_ID,
            temperature=0.3,
        )
        return {item["id"]: resp.choices[0].message.content.strip()}
    except Exception as e:
        print(f"\n  Error on {item['id']}: {e}")
        if "rate_limit" in str(e).lower():
            time.sleep(60)
        return None

def translate_batch(batch):
    if len(batch) == 1:
        return translate_single(batch[0])

    prompt_data = [{"id": b["id"], "text": b["fr_text"]} for b in batch]
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_BATCH},
                {"role": "user", "content": json.dumps(prompt_data, ensure_ascii=False)}
            ],
            model=MODEL_ID,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content.strip()
        data = json.loads(raw)
        return {r["id"]: r["text"] for r in data.get("results", [])}
    except Exception as e:
        print(f"\n  Batch error: {e}")
        if "rate_limit" in str(e).lower():
            time.sleep(60)
        # Fallback: one at a time
        results = {}
        for item in batch:
            r = translate_single(item)
            if r:
                results.update(r)
            time.sleep(DELAY_SECONDS)
        return results

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        to_repair = json.load(f)

    # Load current main text checkpoint
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    # Filter already repaired (in case of resume)
    # We track repairs via a sidecar file to avoid re-running good IDs
    sidecar = "checkpoint_main_text_repaired_ids.json"
    if os.path.exists(sidecar):
        with open(sidecar, "r") as f:
            repaired_ids = set(json.load(f))
    else:
        repaired_ids = set()

    remaining = [item for item in to_repair if item["id"] not in repaired_ids]
    batches = build_smart_batches(remaining)

    solo = sum(1 for b in batches if len(b) == 1)
    print(f"Main Text Repair Report:")
    print(f"  Total remaining : {len(remaining)} segments")
    print(f"  Total batches   : {len(batches)}")
    print(f"  Solo (long)     : {solo}")
    print(f"  Packed (short)  : {len(batches) - solo}")
    print(f"  Est. time       : {len(batches) * DELAY_SECONDS / 60:.0f} min")
    print()

    for i, batch in enumerate(batches):
        ids = [b["id"] for b in batch]
        label = ids[0].split("root.text.")[-1] if len(ids) == 1 else f"{len(ids)} segments"
        print(f"[{i+1}/{len(batches)}] {label}...", end="", flush=True)

        result = translate_batch(batch)

        if result:
            all_results.update(result)
            repaired_ids.update(result.keys())

            # Atomic save both files
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            with open(sidecar, "w") as f:
                json.dump(list(repaired_ids), f)

            print(f" Done.")
        else:
            print(" FAILED.")

        time.sleep(DELAY_SECONDS)

    print(f"\nMain text repair complete. {len(repaired_ids)} segments repaired.")

if __name__ == "__main__":
    main()
