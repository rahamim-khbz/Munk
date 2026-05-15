import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get('VITE_GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_TRANS = 'llama-3.3-70b-versatile'

SYSTEM_PROMPT = '''Translate French to English. Adopt a serious Victorian scholarly prose style.
Return ONLY a JSON object where the key is the same as the input and the value is the English translation.
'''

def translate_preface():
    with open("preface_cleaned.json", "r", encoding="utf-8") as f:
        paragraphs = json.load(f)
        
    print(f"Translating {len(paragraphs)} paragraphs...")
    
    translated_paras = []
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    for i, p in enumerate(paragraphs):
        chunk = {str(i): p}
        user_msg = f"TRANSLATE THESE SEGMENTS:\n{json.dumps(chunk, ensure_ascii=False, indent=2)}"
        
        payload = {
            "model": MODEL_TRANS,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        print(f"Translating paragraph {i+1}...")
        
        success = False
        while not success:
            try:
                response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
                if response.status_code == 429:
                    print("Rate limit, waiting 10s...")
                    time.sleep(10)
                    continue
                    
                response.raise_for_status()
                res_data = response.json()
                raw_text = res_data["choices"][0]["message"]["content"].strip()
                parsed = json.loads(raw_text)
                
                translated_paras.append(parsed[str(i)])
                success = True
                time.sleep(2)  # small delay
                
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
                
    # Now add to checkpoint_main_text_groq.json
    checkpoint_file = "checkpoint_main_text_groq.json"
    with open(checkpoint_file, "r", encoding="utf-8") as f:
        corpus = json.load(f)
        
    for i, tp in enumerate(translated_paras):
        corpus[f"root.text.Munk's Introduction.{i}"] = tp
        
    # Also save the french ones to something if needed?
    # No, the UI handles English/Hebrew. Wait, user wants French and English alongside.
    # The build script expects Hebrew and English. For Munk's intro, we can put French in the Hebrew cell.
    # We should save French paragraphs somewhere too. Let's create a french JSON so build script can read it,
    # or just inject them directly in build_full_viewer.py.
    # Let's save the translations first.
    
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
        
    print("Done! Appended to checkpoint_main_text_groq.json.")
    
if __name__ == "__main__":
    translate_preface()
