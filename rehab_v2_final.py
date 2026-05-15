
import json
import time
import os
import re
from google import genai
from google.genai import types

# --- CONFIGURATION ---
BATCH_SIZE = 30
MODEL_ID = "gemini-3-flash-preview" # Using the user's preferred model
INPUT_FILE = "repair_list.json"
OUTPUT_FILE = "checkpoint_footnotes_gemini_rehab.json"
SYSTEM_PROMPT = """You are an elite scholarly translator for Salomon Munk’s 19th-century commentary on Maimonides.
MISSION: Translate French footnotes into high-fidelity English.
CONSTRAINTS:
1. Preserve all [[t:N]] and [[fn:N]] tags exactly.
2. Maintain dense academic tone.
3. Use your 64k output buffer to ensure NO truncation.
4. Output JSON ONLY: {"results": [{"id": "...", "text": "...", "en_words": ...}]}"""

# Load .env if it exists
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY="):
                os.environ["GOOGLE_API_KEY"] = line.split("=")[1].strip()

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_word_count(text):
    return len(re.findall(r'\w+', text))

def process_batch(batch):
    prompt = f"Translate the following footnotes. Return JSON only.\n\n{json.dumps(batch, ensure_ascii=False)}"
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=64000,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        # Clean up the response text if it has markdown blocks
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        
        return json.loads(raw_text)
    except Exception as e:
        print(f"Error processing batch: {e}")
        return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        to_repair = json.load(f)

    # Load existing progress if any
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = {}

    total = len(to_repair)
    print(f"Starting rehabilitation of {total} footnotes...")

    for i in range(0, total, BATCH_SIZE):
        batch = to_repair[i:i+BATCH_SIZE]
        batch_ids = [f['id'] for f in batch]
        
        # Skip if all IDs in batch are already in all_results
        if all(fid in all_results for fid in batch_ids):
            print(f"Skipping batch {i//BATCH_SIZE + 1} (already done)")
            continue

        print(f"Processing batch {i//BATCH_SIZE + 1} ({i}/{total})...")
        
        # Prepare batch for model (send ID and FR text)
        model_input = [{"id": b["id"], "text": b["fr_text"]} for b in batch]
        
        outcome = process_batch(model_input)
        
        if outcome and "results" in outcome:
            for res in outcome["results"]:
                all_results[res["id"]] = res["text"]
            
            # Save checkpoint
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"  Batch {i//BATCH_SIZE + 1} saved.")
        else:
            print(f"  Batch {i//BATCH_SIZE + 1} FAILED. Retrying next time.")
        
        # Brief pause for rate limits
        time.sleep(2)

    print("Rehabilitation complete.")

if __name__ == "__main__":
    main()
