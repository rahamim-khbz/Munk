
import json
import os
import re
import time
from groq import Groq

# --- CONFIGURATION ---
MODEL_ID = "llama-3.1-8b-instant"
OUTPUT_FILE = "checkpoint_footnotes_rehab_groq.json"
DELAY_SECONDS = 5
MAX_BATCH_WORDS = 400  # Target: keep combined input under ~600 tokens

def load_env():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
client = Groq(api_key=os.environ.get("VITE_GROQ_API_KEY"))

SYSTEM_PROMPT_SINGLE = """You are an elite scholarly translator for Salomon Munk.
Translate the French footnote into high-fidelity English.
CONSTRAINTS:
1. Preserve all [[t:N]] and [[fn:N]] tags exactly.
2. Maintain dense academic tone.
3. Output the translated text ONLY."""

SYSTEM_PROMPT_BATCH = """You are an elite scholarly translator for Salomon Munk.
Translate each French footnote into high-fidelity English.
CONSTRAINTS:
1. Preserve all [[t:N]] and [[fn:N]] tags exactly.
2. Maintain dense academic tone.
3. Output JSON ONLY: {"results": [{"id": "fn.X", "text": "..."}]}"""

def get_word_count(text):
    return len(re.findall(r'\w+', text))

def build_smart_batches(items):
    """Pack short footnotes together, send long ones alone."""
    batches = []
    current_batch = []
    current_words = 0
    
    # Sort by word count ascending so short ones cluster together
    items_sorted = sorted(items, key=lambda x: get_word_count(x["fr_text"]))
    
    for item in items_sorted:
        wc = get_word_count(item["fr_text"])
        
        # Long footnotes (>300 words) always go alone
        if wc > 300:
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_words = 0
            batches.append([item])
            continue
        
        # Can we fit this in the current batch?
        if current_words + wc <= MAX_BATCH_WORDS and len(current_batch) < 5:
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
    """Translate a single footnote (for long ones)."""
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
    """Translate a small batch of short footnotes."""
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
        results = {}
        for r in data.get("results", []):
            results[r["id"]] = r["text"]
        return results
    except Exception as e:
        print(f"\n  Batch error: {e}")
        if "rate_limit" in str(e).lower():
            time.sleep(60)
        # Fallback: try one at a time
        results = {}
        for item in batch:
            r = translate_single(item)
            if r:
                results.update(r)
            time.sleep(DELAY_SECONDS)
        return results

def main():
    # Load full French source
    with open("French_Arabic_Enriched.json", "r", encoding="utf-8") as f:
        fr_data = json.load(f)
    from munk_pipeline_groq import extract_and_flatten
    _, fr_fns = extract_and_flatten(fr_data)
    
    all_items = [{"id": k, "fr_text": v["text"]} for k, v in fr_fns.items()]
    
    # Load existing progress
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = {}

    # Filter out already done
    remaining = [item for item in all_items if item["id"] not in all_results]
    
    # Build smart batches
    batches = build_smart_batches(remaining)
    
    total_fns = len(remaining)
    total_batches = len(batches)
    solo_batches = sum(1 for b in batches if len(b) == 1)
    packed_batches = total_batches - solo_batches
    
    print(f"Smart Packing Report:")
    print(f"  Total remaining: {total_fns} footnotes")
    print(f"  Total batches: {total_batches}")
    print(f"  Solo (long): {solo_batches}")
    print(f"  Packed (short): {packed_batches} (avg {total_fns/max(total_batches,1):.1f} fns/batch)")
    print(f"  Est. time: {total_batches * DELAY_SECONDS / 60:.0f} min")
    print()

    done_count = 0
    for i, batch in enumerate(batches):
        ids = [b["id"] for b in batch]
        label = ",".join(ids) if len(ids) <= 3 else f"{ids[0]}...{ids[-1]}"
        print(f"[{i+1}/{total_batches}] {label} ({len(batch)} fns)...", end="", flush=True)
        
        result = translate_batch(batch)
        
        if result:
            all_results.update(result)
            done_count += len(result)
            
            # Atomic save every batch
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f" Done. ({len(all_results)}/{len(all_items)} total)")
        else:
            print(" FAILED.")
        
        time.sleep(DELAY_SECONDS)

    print(f"\nRehabilitation complete. {len(all_results)}/{len(all_items)} footnotes translated.")

if __name__ == "__main__":
    main()
