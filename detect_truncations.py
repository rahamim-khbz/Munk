
import json
import re

def detect_truncation(text, fr_word_count):
    if not text: return "Empty"
    
    # 1. Dangling Tags (e.g. "[[t:6" at the end)
    if text.endswith("[") or text.endswith("[[") or re.search(r'\[\[[a-z]:\d+$', text):
        return "Dangling Tag"
    
    # 2. Incomplete Sentence (doesn't end with punctuation)
    # We allow closing brackets/quotes after punctuation
    if not re.search(r'[.!?!"\']\s*$', text) and not text.endswith("]]"):
        # Special check for footnotes that might end with a year or page number
        if not re.search(r'\d+\.?$', text):
            return "Incomplete Sentence"
    
    # 3. Severe Word Count Drop
    en_word_count = len(re.findall(r'\w+', text))
    if fr_word_count > 50 and (en_word_count / fr_word_count) < 0.5:
        return "Severe Word Count Drop"

    return None

def main():
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        english_fns = json.load(f)
    
    # We need the French word counts to calculate ratios
    # I'll use the already extracted flat_fns logic
    from munk_pipeline_groq import extract_and_flatten
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)
    _, flat_fns = extract_and_flatten(french_data)

    truncated = []
    for fid, info in flat_fns.items():
        fr_text = info['text']
        fr_word_count = len(re.findall(r'\w+', fr_text))
        
        # English might be split into .sub_N
        en_text = ""
        if fid in english_fns:
            en_text = english_fns[fid]
        else:
            sub_id = f"{fid}.sub_0"
            if sub_id in english_fns:
                # Combine sub-parts for health check
                parts = []
                idx = 0
                while f"{fid}.sub_{idx}" in english_fns:
                    parts.append(english_fns[f"{fid}.sub_{idx}"])
                    idx += 1
                en_text = " ".join(parts)
        
        reason = detect_truncation(en_text, fr_word_count)
        if reason:
            truncated.append({
                "id": fid,
                "reason": reason,
                "fr_words": fr_word_count,
                "en_words": len(re.findall(r'\w+', en_text)),
                "snippet": en_text[-50:] if en_text else ""
            })

    print(f"Found {len(truncated)} potentially truncated footnotes.")
    print("| Footnote ID | Reason | FR Words | EN Words | Ending Snippet |")
    print("|---|---|---|---|---|")
    for t in truncated:
        print(f"| {t['id']} | {t['reason']} | {t['fr_words']} | {t['en_words']} | `{t['snippet']}` |")

if __name__ == "__main__":
    main()
