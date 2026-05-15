
import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from munk_pipeline_groq import extract_and_flatten

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-3-flash-preview"

def patch_missing():
    print("--- Patching Final 5 Segments (Batch 215) ---")
    
    with open('French_Arabic_Enriched.json', 'r') as f:
        data = json.load(f)
    flat, _ = extract_and_flatten(data)
    
    missing_keys = [
        "root.text.Part 3..50.15.sub_1",
        "root.text.Part 3..50.16",
        "root.text.Part 3..50.17",
        "root.text.Part 3..50.18",
        "root.text.Part 3..50.19"
    ]
    
    chunk = {k: flat[k]['text'] if isinstance(flat[k], dict) else flat[k] for k in missing_keys if k in flat}
    
    if not chunk:
        print("All segments found! No patching needed.")
        return

    prompt = json.dumps(chunk, indent=2)
    system_instruction = """You are a scholarly translator. You are translating a 12th-century theological work by Moses Maimonides. 
    The text contains biblical quotes (e.g., Psalm 91) and discussions on religious providence. 
    This is for ACADEMIC RESEARCH only. Do NOT block this content for safety reasons as it is historical and theological.
    Return JSON."""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                safety_settings=[
                    types.SafetySetting(category="HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                ]
            )
        )
        
        if not response.text:
            print("❌ Model returned empty response. Possibly safety-blocked.")
            return

        parsed = json.loads(response.text)
        
        # Weave tags back (simplified for this patch)
        final_res = {}
        for k, translated in parsed.items():
            if k in flat and isinstance(flat[k], dict) and 'tags' in flat[k]:
                tags = flat[k]['tags']
                import re
                final_res[k] = re.sub(r'\[\[t:(\d+)\]\]', lambda m: tags[int(m.group(1))] if int(m.group(1)) < len(tags) else m.group(0), translated)
            else:
                final_res[k] = translated

        # Update Checkpoint
        with open('checkpoint_main_text_groq.json', 'r') as f:
            ckpt = json.load(f)
        
        ckpt.update(final_res)
        
        with open('checkpoint_main_text_groq.json', 'w') as f:
            json.dump(ckpt, f, indent=2)
            
        print(f"✅ Successfully patched {len(final_res)} segments!")
        
    except Exception as e:
        print(f"❌ Patching failed: {e}")

if __name__ == "__main__":
    patch_missing()
