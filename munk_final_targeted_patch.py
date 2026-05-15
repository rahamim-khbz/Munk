
import os
import json
import time
import re
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
FRENCH_SOURCE = "French_Arabic_Enriched.json"

TARGET_IDS = ["fn.3698", "fn.3699", "fn.3708", "fn.3709", "fn.3710", "fn.3711", "fn.3712", "fn.3722", "fn.3723", "fn.2186"]

FOOTNOTE_SYSTEM_PROMPT = """You are a master scholarly translator. 
Translate Salomon Munk's 'Le Guide des Égarés' FOOTNOTES into precise Academic English.
Rules:
1. Preserve markers like [[t:N]] exactly.
2. Maintain Hebrew/Arabic script.
3. Return ONLY a valid JSON object mapping the input keys to translated strings.
"""

def call_gemini_single(fid, text, tags, system_prompt):
    chunk = {fid: text}
    prompt = json.dumps(chunk, indent=2)
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
        
        translated_text = parsed.get(fid, "")
        if translated_text:
            # Re-weave tags
            def tag_sub(m):
                tid = int(m.group(1))
                return tags[tid] if tid < len(tags) else m.group(0)
            return re.sub(r'\[\[t:(\d+)\]\]', tag_sub, translated_text)
    except Exception as e:
        print(f"  [Error] {fid} failed: {e}")
    return None

def main():
    print("--- Final Targeted Footnote Patch ---")
    with open(FRENCH_SOURCE, 'r') as f:
        french_data = json.load(f)
    
    print("Extracting original footnotes...")
    _, flat_footnotes = extract_and_flatten(french_data)
    
    with open(FN_CHECKPOINT, 'r') as f:
        fn_checkpoint = json.load(f)

    for fid in TARGET_IDS:
        if fid not in flat_footnotes:
            # Check if it's a split base
            base_info = [v for k, v in flat_footnotes.items() if k.startswith(f"{fid}.")]
            if base_info:
                print(f"Repairing multi-part footnote: {fid}")
                # Re-translate each part separately
                for sub_fid in sorted([k for k in flat_footnotes if k.startswith(f"{fid}.")]):
                    info = flat_footnotes[sub_fid]
                    print(f"  Processing {sub_fid}...")
                    res = call_gemini_single(sub_fid, info['text'], info['tags'], FOOTNOTE_SYSTEM_PROMPT)
                    if res:
                        fn_checkpoint[sub_fid] = res
            continue
            
        print(f"Repairing {fid}...")
        info = flat_footnotes[fid]
        res = call_gemini_single(fid, info['text'], info['tags'], FOOTNOTE_SYSTEM_PROMPT)
        if res:
            fn_checkpoint[fid] = res
            # Remove any sub-parts if this was a poison/gap fix
            to_del = [sk for sk in fn_checkpoint if sk.startswith(f"{fid}.sub_")]
            for sk in to_del: del fn_checkpoint[sk]
        
        # Immediate save
        with open(FN_CHECKPOINT, 'w') as f:
            json.dump(fn_checkpoint, f, indent=2)
        time.sleep(1)

    print("Targeted patch complete.")

if __name__ == "__main__":
    main()
