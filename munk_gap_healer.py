
import json
import os
import re
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("VITE_GROQ_API_KEY"))

# Aligned Prompt to avoid Latin-only outputs
TRANSLATOR_PROMPT = """You are a master scholarly translator specializing in French academic prose and medieval philosophical texts.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' segments into precise Academic English.

Tone: Modern Academic Scholarly (precise, formal, clear).
Rules:
1. Use formal academic vocabulary. Avoid archaic or "old-sounding" English.
2. NO EXTERNAL KNOWLEDGE: Translate ONLY what is in the provided French text.
3. If the French text contains Latin citations or phrases, translate them into English. You may preserve the original Latin in brackets [Lat.: ...] following the English translation, but the segment must be primarily English.
4. Do NOT translate Hebrew/Arabic scripts if present; preserve them exactly.
5. Use standard modern scholarly conventions for citations (e.g., 'See', 'Cf.', 'Note').
6. DO NOT ADD ANY PREAMBLE. Return only the translated text."""

ALIGNER_PROMPT_TEMPLATE = """I have a French sentence with [[t:N]] or [[fn:N]] markers and its English translation.
Your task is to re-insert the markers into the English translation in the exact same semantic positions.

French (Original): {french}
English (Translated): {english}

Return ONLY the English text with markers. No preamble."""

def identify_latin_only(text):
    if not text: return True
    clean = re.sub(r'\[Lat\.:.*?\]', '', text)
    clean = re.sub(r'\[\[.*?\]\]', '', clean)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = clean.strip()
    return len(clean) < 5 and "[Lat.:" in text

def heal_worker(seg_id, french_text):
    """Two-pass heal using Groq."""
    naked_french = re.sub(r'\[\[.*?\]\]', '', french_text)
    
    for attempt in range(3):
        try:
            # Pass 1: Translate
            chat_1 = client.chat.completions.create(
                messages=[{"role": "system", "content": TRANSLATOR_PROMPT}, {"role": "user", "content": naked_french}],
                model="llama-3.3-70b-versatile",
                max_tokens=4096,
                temperature=0.1
            )
            en_naked = chat_1.choices[0].message.content.strip()
            
            # Pass 2: Re-tag
            chat_2 = client.chat.completions.create(
                messages=[{"role": "user", "content": ALIGNER_PROMPT_TEMPLATE.format(french=french_text, english=en_naked)}],
                model="llama-3.1-8b-instant",
                max_tokens=4096,
                temperature=0.1
            )
            final = chat_2.choices[0].message.content.strip()
            return final
        except Exception as e:
            print(f"  [Error] {seg_id} heal attempt {attempt+1}: {e}")
            time.sleep(10)
    return None

def run_healer():
    print("=== Munk Gap Healer: Fixing Latin-only & Missing Segments ===")
    
    # 1. Load Everything
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)
    with open("checkpoint_main_text_groq.json", "r") as f:
        english_main = json.load(f)
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        english_fns = json.load(f)
    
    from munk_pipeline_groq import extract_and_flatten
    flat_fr_main, flat_fr_fns = extract_and_flatten(french_data)
    
    # 2. Identify Targets
    targets_main = []
    for seg_id, fr_info in flat_fr_main.items():
        en = english_main.get(seg_id)
        if not en or identify_latin_only(en):
            targets_main.append(seg_id)
            
    targets_fns = []
    for fn_id, fr_info in flat_fr_fns.items():
        en = english_fns.get(fn_id)
        if not en or identify_latin_only(en):
            targets_fns.append(fn_id)

    print(f"  [Healer] Targets: {len(targets_main)} main segments, {len(targets_fns)} footnotes.")
    
    # 3. Heal Main Text
    for i, seg_id in enumerate(targets_main):
        print(f"  [Healing Main] {seg_id} ({i+1}/{len(targets_main)})")
        fr_text = flat_fr_main[seg_id]['text']
        res = heal_worker(seg_id, fr_text)
        if res:
            english_main[seg_id] = res
            with open("checkpoint_main_text_groq.json", "w") as f:
                json.dump(english_main, f, indent=2)
    
    # 4. Heal Footnotes
    for i, fn_id in enumerate(targets_fns):
        print(f"  [Healing FN] {fn_id} ({i+1}/{len(targets_fns)})")
        fr_text = flat_fr_fns[fn_id]['text']
        res = heal_worker(fn_id, fr_text)
        if res:
            english_fns[fn_id] = res
            with open("checkpoint_footnotes_gemini.json", "w") as f:
                json.dump(english_fns, f, indent=2)

    print("=== Healer Finished ===")

if __name__ == "__main__":
    run_healer()
