
import os
import json
import time
import re
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from munk_pipeline_groq import extract_and_flatten

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-flash-preview" 
client = genai.Client(api_key=GOOGLE_API_KEY)

FN_CHECKPOINT = "checkpoint_footnotes_gemini.json"
MAIN_CHECKPOINT = "checkpoint_main_text_groq.json"
FRENCH_SOURCE = "French_Arabic_Enriched.json"

# --- PROMPTS ---

MAIN_SYSTEM_PROMPT = """You are a master scholarly translator specializing in French academic prose and medieval philosophical texts.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' into precise Academic English.

Tone: Modern Academic Scholarly (precise, formal, clear).
Rules:
1. Preserve all markers like [[t:N]] and [[fn:N]] EXACTLY in their correct relative positions. 
2. Maintain Hebrew and Arabic scripts exactly.
3. Use formal academic vocabulary. Avoid archaic English.
4. Return ONLY a valid JSON object mapping the input keys to translated strings.
"""

FOOTNOTE_SYSTEM_PROMPT = """You are a master scholarly translator.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' FOOTNOTES into precise Academic English.

Tone: Modern Academic Scholarly.
Rules:
1. Preserve markers like [[t:N]] or [[fn:ID]] exactly.
2. Do not translate Hebrew/Arabic scripts.
3. Use standard modern scholarly conventions for citations (e.g., 'See', 'Cf.', 'Note').
4. Return ONLY a valid JSON object mapping the input keys to translated strings.
"""

def call_gemini(chunk, system_prompt):
    """Translates a batch of segments using Gemini 3 Flash."""
    # Prepare lean prompt
    lean_chunk = {k: v['text'] if isinstance(v, dict) else v for k, v in chunk.items()}
    prompt = json.dumps(lean_chunk, indent=2)
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                )
            )
            
            raw_text = response.text.strip()
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match: raw_text = json_match.group(0)
            
            parsed = json.loads(raw_text)
            
            # Re-weave Tags
            final_res = {}
            for k, translated_text in parsed.items():
                if k in chunk and isinstance(chunk[k], dict) and 'tags' in chunk[k]:
                    original_tags = chunk[k]['tags']
                    def tag_sub(m):
                        tid = int(m.group(1))
                        return original_tags[tid] if tid < len(original_tags) else m.group(0)
                    
                    final_res[k] = re.sub(r'\[\[t:(\d+)\]\]', tag_sub, translated_text)
                else:
                    final_res[k] = translated_text
            
            return final_res
            
        except Exception as e:
            print(f"  [Error] Gemini Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return None

def count_words(text):
    if not text: return 0
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\[\[fn:\d+\]\]', '', clean)
    clean = re.sub(r'\[\[t:\d+\]\]', '', clean)
    return len(clean.split())

def main():
    print("--- Munk Rehabilitation (Gemini 3 Flash Preview) ---")
    
    if not os.path.exists(FRENCH_SOURCE):
        print("French source not found.")
        return

    with open(FRENCH_SOURCE, 'r') as f:
        french_data = json.load(f)
    
    print("Flattening French source...")
    flat_main, flat_footnotes = extract_and_flatten(french_data)
    
    # Load translated data
    with open(FN_CHECKPOINT, 'r') as f: trans_fns = json.load(f)
    with open(MAIN_CHECKPOINT, 'r') as f: main_trans = json.load(f)

    # 1. Identify missing/poison footnotes
    todo_fns = {}
    for fid, info in flat_footnotes.items():
        text = info['text']
        if fid not in trans_fns:
            todo_fns[fid] = info
        else:
            # Check for poison/truncation
            trans_text = trans_fns[fid]
            orig_count = count_words(text)
            trans_count = count_words(trans_text)
            if orig_count > 10:
                ratio = trans_count / orig_count
                if ratio < 0.4 or ratio > 2.5:
                    print(f"  [Poison FN] {fid} ({orig_count} -> {trans_count} words, ratio {ratio:.2f})")
                    todo_fns[fid] = info

    # 2. Identify mismatched main text
    todo_main = {}
    for path, info in flat_main.items():
        orig_text = info['text']
        orig_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', orig_text))
        
        if path not in main_trans:
            todo_main[path] = info
        else:
            trans_text = main_trans[path]
            trans_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', trans_text))
            if orig_fn_count != trans_fn_count:
                print(f"  [Mismatch Main] {path} ({orig_fn_count} vs {trans_fn_count} markers)")
                todo_main[path] = info

    print(f"\nTasks identified:")
    print(f"- Footnotes to fix: {len(todo_fns)}")
    print(f"- Main text segments to fix: {len(todo_main)}")

    # EXECUTE REPAIRS
    if todo_fns:
        print("\n=== Fixing Footnotes ===")
        items = list(todo_fns.items())
        # Batch size 10
        for i in range(0, len(items), 10):
            batch = dict(items[i:i+10])
            first_key = list(batch.keys())[0]
            print(f"  Batch {i//10 + 1}/{(len(items)-1)//10 + 1} ({first_key})...")
            res = call_gemini(batch, FOOTNOTE_SYSTEM_PROMPT)
            if res:
                trans_fns.update(res)
                with open(FN_CHECKPOINT, 'w') as f:
                    json.dump(trans_fns, f, indent=2)
            time.sleep(2)

    if todo_main:
        print("\n=== Fixing Main Text Segments ===")
        items = list(todo_main.items())
        # Batch size 5
        for i in range(0, len(items), 5):
            batch = dict(items[i:i+5])
            first_key = list(batch.keys())[0]
            print(f"  Batch {i//5 + 1}/{(len(items)-1)//5 + 1} ({first_key})...")
            res = call_gemini(batch, MAIN_SYSTEM_PROMPT)
            if res:
                main_trans.update(res)
                with open(MAIN_CHECKPOINT, 'w') as f:
                    json.dump(main_trans, f, indent=2)
            time.sleep(2)

    print("\nRehabilitation complete. Checking status...")
    # Optional: run audit again
    # subprocess.run(["python3", "audit_footnotes_detailed.py"])

if __name__ == "__main__":
    main()
