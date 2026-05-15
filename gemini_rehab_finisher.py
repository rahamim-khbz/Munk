
import os
import json
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
MODEL_ID = "gemini-2.5-flash"
SOURCE_FILE = "French_Arabic_Enriched.json"
CHECKPOINT_FILE = "checkpoint_footnotes_rehab_groq.json"
DELAY_SECONDS = 1.0  # Gemini is faster but we respect RPM limits

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """You are an elite scholarly translator rendering Salomon Munk's 19th-century French footnotes into scholarly English.
CONSTRAINTS:
1. Preserve ALL [[t:N]] and [[fn:N]] markers exactly.
2. Preserve ALL Hebrew, Arabic, and Greek script exactly.
3. Translate Latin inline as [Lat.: ...].
4. Use formal scholarly prose ('one' over 'we', 'doubtless' over 'likely'), but DO NOT use overly archaic verbal endings like '-eth' (use 'bears' not 'beareth').
5. Output ONLY a JSON object: {"results": [{"id": "fn.N", "text": "..."}]}"""

def get_word_count(text):
    return len(re.findall(r'\w+', text))

def build_batches(items, max_words=1000, max_items=8):
    batches = []
    current_batch = []
    current_words = 0
    for item in items:
        wc = get_word_count(item['text'])
        if (current_words + wc > max_words or len(current_batch) >= max_items) and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_words = 0
        current_batch.append(item)
        current_words += wc
    if current_batch:
        batches.append(current_batch)
    return batches

def main():
    print("=== Munk Footnote Finisher (Gemini Track) ===")
    
    # 1. Load French source
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        fr_data = json.load(f)
    
    # Import flattener from existing script
    import sys
    sys.path.append(os.getcwd())
    from munk_pipeline_groq import extract_and_flatten
    _, fr_fns_map = extract_and_flatten(fr_data)
    
    # 2. Load Progress
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            done_fns = json.load(f)
    else:
        done_fns = {}
        
    remaining_ids = [fid for fid in fr_fns_map if fid not in done_fns]
    if not remaining_ids:
        print("✅ All footnotes already rehabilitated!")
        return

    print(f"  Progress: {len(done_fns)} done, {len(remaining_ids)} remaining.")
    
    remaining_items = [{"id": fid, "text": fr_fns_map[fid]['text']} for fid in remaining_ids]
    batches = build_batches(remaining_items)
    print(f"  Batching into {len(batches)} groups.")

    model = genai.GenerativeModel(
        model_name=MODEL_ID,
        system_instruction=SYSTEM_PROMPT
    )

    for i, batch in enumerate(batches):
        print(f"[{i+1}/{len(batches)}] Processing {len(batch)} fns ({batch[0]['id']}...)...", end="", flush=True)
        
        user_msg = json.dumps(batch, ensure_ascii=False)
        
        try:
            response = model.generate_content(
                user_msg,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            
            res_data = json.loads(response.text)
            for r in res_data.get("results", []):
                done_fns[r["id"]] = r["text"]
            
            # Atomic save
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(done_fns, f, indent=2, ensure_ascii=False)
            
            print(f" Done. ({len(done_fns)} total)")
            
        except Exception as e:
            print(f" FAILED: {e}")
            time.sleep(10)
            
        time.sleep(DELAY_SECONDS)

    print("\n✅ Final rehabilitation complete!")

if __name__ == "__main__":
    main()
