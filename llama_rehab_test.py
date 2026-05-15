import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("VITE_GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

TEST_CASES = [
    {
        "id": "fn.0",
        "text": "Nous avons traduit ici les mots [[t:0]]\u05d0\u05dc \u05e2\u05d5\u05dc\u05dd[[t:1]] dans le sens que Ma\u00efmonide lui-m\u00eame leur pr\u00eate dans plusieurs endroits, et notamment dans le chap. 29 de la troisi\u00e8me partie du [[t:2]]Guide[[t:3]], quoique dans le passage biblique (Gen\u00e8se, 21, 33) ces mots signifient [[t:4]]le Dieu \u00e9ternel[[t:5]].",
        "tags": ["<span dir=\"rtl\">", "</span>", "<i>", "</i>", "<i>", "</i>"]
    },
    {
        "id": "fn.1",
        "text": "Le verbe [[t:0]]\u05db\u05e0\u05ea[[t:1]] [[t:2]](\u0643\u064f\u0646\u0652\u062a\u064e)[[t:3]]  qui commence la phrase se rapporte aux mots [[t:4]]\u05e2\u05d8\u05c4\u05dd \u05e9\u05d0\u05e0\u05da[[t:5]], qu\u2019il sert \u00e0 mettre au plus-que-parfait.",
        "tags": ["<span dir=\"rtl\">", "</span>", "<span dir=\"rtl\">", "</span>", "<span dir=\"rtl\">", "</span>"]
    }
]

SYSTEM_PROMPT = """You are a master scholarly translator specializing in 19th-century French academic prose. 
Translate the following French text into Victorian English. 
Do not translate the Hebrew/Arabic scripts if present."""

def run_direct_test(text):
    print(f"\n--- Running Direct Translation (Baseline) ---")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Maintain markers like [[t:N]] exactly."},
            {"role": "user", "content": text}
        ],
        model=MODEL,
    )
    return chat_completion.choices[0].message.content

def run_mirror_test(text):
    print(f"\n--- Running Mirror Pass (Rehab) ---")
    
    # Pass 1: Translate Naked Text (Tags removed)
    naked_text = re.sub(r'\[\[t:\d+\]\]', '', text)
    
    print(f"  [Pass 1] Input: {naked_text}")
    chat_1 = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": naked_text}
        ],
        model=MODEL,
    )
    translated_naked = chat_1.choices[0].message.content
    print(f"  [Result 1] {translated_naked}")
    
    # Pass 2: The Aligner
    print("  [Pass 2] Aligning Tags...")
    aligner_prompt = f"""I have a French sentence with [[t:N]] markers and its English translation.
Your task is to re-insert the [[t:N]] markers into the English translation in the exact same semantic positions.

French (Original): {text}
English (Translated): {translated_naked}

Return ONLY the English text with markers. No preamble."""

    chat_2 = client.chat.completions.create(
        messages=[
            {"role": "user", "content": aligner_prompt}
        ],
        model=MODEL,
    )
    return chat_2.choices[0].message.content

def main():
    for case in TEST_CASES:
        print(f"\n========================================")
        print(f"TEST CASE: {case['id']}")
        print(f"SOURCE: {case['text']}")
        
        direct = run_direct_test(case['text'])
        print(f"DIRECT RESULT: {direct}")
        
        mirror = run_mirror_test(case['text'])
        print(f"MIRROR RESULT: {mirror}")

if __name__ == "__main__":
    main()
