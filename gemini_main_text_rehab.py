
import os
import json
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
MODEL_ID = "gemini-2.5-flash"
INPUT_FILE = "main_text_repair_list.json"
OUTPUT_FILE = "checkpoint_main_text_groq.json"
SIDECAR_FILE = "checkpoint_main_text_repaired_ids.json"
DELAY_SECONDS = 1.0
MAX_BATCH_WORDS = 800  # Gemini has a larger context window than llama-8b

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

SYSTEM_PROMPT_SINGLE = """You are an elite scholarly translator rendering Salomon Munk's 19th-century French into Victorian scholarly English.
CONSTRAINTS:
1. Preserve ALL [[t:N]] and [[fn:N]] markers exactly as they appear — do not alter, move, or remove them.
2. Preserve ALL Hebrew, Arabic, and Greek script exactly.
3. Translate Latin inline as [Lat.: ...].
4. Use formal Victorian scholarly prose: prefer 'one' over 'we', 'doubtless' over 'likely', passive constructions where appropriate.
5. DO NOT use archaic verbal endings like '-eth' (use 'bears' not 'beareth').
6. Output the translated text ONLY. No preamble."""

SYSTEM_PROMPT_BATCH = """You are an elite scholarly translator rendering Salomon Munk's 19th-century French into Victorian scholarly English.
Translate each segment. CONSTRAINTS:
1. Preserve ALL [[t:N]] and [[fn:N]] markers exactly.
2. Preserve ALL Hebrew, Arabic, and Greek script exactly.
3. Translate Latin inline as [Lat.: ...].
4. Use formal Victorian scholarly prose. DO NOT use archaic verbal endings like '-eth'.
5. Output JSON ONLY: {"results": [{"id": "...", "text": "..."}]}"""

def get_word_count(text):
    return len(re.findall(r'\w+', text))

def build_smart_batches(items):
    batches = []
    current_batch = []
    current_words = 0

    # Sort ascending by word count
    items_sorted = sorted(items, key=lambda x: get_word_count(x["fr_text"]))

    for item in items_sorted:
        wc = get_word_count(item["fr_text"])

        if wc > 400:  # Long segments go alone
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_words = 0
            batches.append([item])
            continue

        if current_words + wc <= MAX_BATCH_WORDS and len(current_batch) < 8:
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

def main():
    print(f"=== Munk Main Text Repair (Gemini Track: {MODEL_ID}) ===")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        to_repair = json.load(f)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = {}

    if os.path.exists(SIDECAR_FILE):
        with open(SIDECAR_FILE, "r") as f:
            repaired_ids = set(json.load(f))
    else:
        repaired_ids = set()

    remaining = [item for item in to_repair if item["id"] not in repaired_ids]
    if not remaining:
        print("✅ No segments remaining for repair.")
        return

    batches = build_smart_batches(remaining)
    print(f"  Remaining: {len(remaining)} segments in {len(batches)} batches.")

    model_single = genai.GenerativeModel(model_name=MODEL_ID, system_instruction=SYSTEM_PROMPT_SINGLE)
    model_batch = genai.GenerativeModel(model_name=MODEL_ID, system_instruction=SYSTEM_PROMPT_BATCH)

    for i, batch in enumerate(batches):
        ids = [b["id"] for b in batch]
        label = ids[0].split("root.text.")[-1] if len(ids) == 1 else f"{len(ids)} segments"
        print(f"[{i+1}/{len(batches)}] {label}...", end="", flush=True)

        try:
            if len(batch) == 1:
                response = model_single.generate_content(batch[0]["fr_text"])
                result = {batch[0]["id"]: response.text.strip()}
            else:
                prompt_data = [{"id": b["id"], "text": b["fr_text"]} for b in batch]
                response = model_batch.generate_content(
                    json.dumps(prompt_data, ensure_ascii=False),
                    generation_config=genai.GenerationConfig(response_mime_type="application/json")
                )
                data = json.loads(response.text)
                result = {r["id"]: r["text"] for r in data.get("results", [])}

            if result:
                all_results.update(result)
                repaired_ids.update(result.keys())

                # Atomic save
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_results, f, indent=2, ensure_ascii=False)
                with open(SIDECAR_FILE, "w") as f:
                    json.dump(list(repaired_ids), f)
                
                print(f" Done.")
            else:
                print(" FAILED (Empty result).")

        except Exception as e:
            print(f" FAILED: {e}")
            time.sleep(5)

        time.sleep(DELAY_SECONDS)

    print(f"\n✅ Main text repair complete. {len(repaired_ids)} segments total.")

if __name__ == "__main__":
    main()
