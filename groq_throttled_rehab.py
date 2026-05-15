
import json
import os
import time
from groq import Groq

# --- THROTTLED CONFIG ---
MODEL_ID = "llama-3.3-70b-versatile"
INPUT_FILE = "repair_list.json"
OUTPUT_FILE = "checkpoint_footnotes_rehab_groq.json"
DELAY_SECONDS = 5  # Stay well under 12k TPM

def load_env():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
client = Groq(api_key=os.environ.get("VITE_GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an elite scholarly translator for Salomon Munk.
Translate the French footnote into high-fidelity English.
CONSTRAINTS:
1. Preserve all [[t:N]] and [[fn:N]] tags exactly.
2. Maintain dense academic tone.
3. Output the translated text ONLY."""

def main():
    with open("French_Arabic_Enriched.json", "r", encoding="utf-8") as f:
        fr_data = json.load(f)
    
    from munk_pipeline_groq import extract_and_flatten
    _, fr_fns = extract_and_flatten(fr_data)
    
    # Convert dict to list of items and sort numerically
    to_repair = [{"id": k, "fr_text": v["text"]} for k, v in fr_fns.items()]
    to_repair.sort(key=lambda x: int(x["id"].split(".")[1]) if "_" not in x["id"] else int(x["id"].split(".")[1]) + 0.1)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = {}

    remaining = [item for item in to_repair if item["id"] not in all_results]
    print(f"Starting throttled rehab for {len(remaining)} footnotes...")

    for i, item in enumerate(remaining):
        fid = item["id"]
        text = item["fr_text"]
        
        print(f"[{i+1}/{len(remaining)}] Processing {fid}...", end="", flush=True)
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                model=MODEL_ID,
                temperature=0.3,
            )
            
            result = chat_completion.choices[0].message.content.strip()
            all_results[fid] = result
            
            # Atomic save
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            print(" Done.")
            
            # Throttle to stay under 12k TPM
            time.sleep(DELAY_SECONDS)
            
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                print("\nRate limit hit! Sleeping for 60s...")
                time.sleep(60)
            else:
                print(f"\nError on {fid}: {e}")
                time.sleep(10)

    print("Rehabilitation complete.")

if __name__ == "__main__":
    main()
