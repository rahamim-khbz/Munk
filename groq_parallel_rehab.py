
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from groq import Groq

# --- CONFIGURATION ---
MAX_WORKERS = 10  # Parallel threads
MODEL_ID = "llama-3.3-70b-versatile"
INPUT_FILE = "repair_list.json"
OUTPUT_FILE = "checkpoint_footnotes_rehab_groq.json"

# Load .env
def load_env():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
client = Groq(api_key=os.environ.get("VITE_GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an elite scholarly translator for Salomon Munk’s 19th-century commentary on Maimonides.
Translate the French footnote into high-fidelity English.
CONSTRAINTS:
1. Preserve all [[t:N]] and [[fn:N]] tags exactly.
2. Maintain dense academic tone.
3. Output the translated text ONLY. No preamble or JSON formatting."""

def translate_footnote(item):
    fid = item["id"]
    text = item["fr_text"]
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            model=MODEL_ID,
            temperature=0.3,
            max_tokens=4096, # Plenty for a single footnote
        )
        return fid, chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error on {fid}: {e}")
        return fid, None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        to_repair = json.load(f)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = {}

    # Filter out already done
    remaining = [item for item in to_repair if item["id"] not in all_results]
    print(f"Starting parallel rehab for {len(remaining)} footnotes ({len(all_results)} already done)...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(translate_footnote, item): item for item in remaining}
        
        count = 0
        for future in as_completed(futures):
            fid, result = future.result()
            if result:
                all_results[fid] = result
                count += 1
                
                # Atomic save every 10 completions
                if count % 10 == 0:
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(all_results, f, indent=2, ensure_ascii=False)
                    print(f"Progress: {len(all_results)}/{len(to_repair)} complete...")

    # Final save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print("Rehabilitation complete.")

if __name__ == "__main__":
    main()
