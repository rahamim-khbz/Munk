
import json
import re

def is_poisoned(en_text, fr_text):
    if not en_text: return True, "Empty"
    
    # 1. Mandatory Structural Flags
    if en_text.endswith("[") or en_text.endswith("[[") or re.search(r'\[\[[a-z]:\d+$', en_text):
        return True, "Dangling Tag"
    
    if not re.search(r'[.!?!"\']\s*$', en_text) and not en_text.endswith("]]"):
         if not re.search(r'\d+\.?$', en_text):
            return True, "Incomplete Sentence"
    
    # 2. Tight Word Count Audit (90% threshold with 5-word failsafe)
    # Use re.findall(r'\w+') to get a clean word count
    fr_words = len(re.findall(r'\w+', fr_text))
    en_words = len(re.findall(r'\w+', en_text))
    
    if fr_words == 0: return False, None
    
    ratio = en_words / fr_words
    delta = fr_words - en_words
    
    if ratio < 0.90 and delta >= 5:
        return True, f"Low Ratio ({ratio:.2f}, Delta: {delta})"
    
    return False, None

def main():
    with open("French_Arabic_Enriched.json", "r", encoding="utf-8") as f:
        fr_data = json.load(f)
    from munk_pipeline_groq import extract_and_flatten
    _, fr_fns = extract_and_flatten(fr_data)

    with open("checkpoint_footnotes_gemini.json", "r", encoding="utf-8") as f:
        en_fns = json.load(f)

    repair_list = []
    
    for fid, info in fr_fns.items():
        fr_text = info['text']
        en_text = en_fns.get(fid, "")
        
        # Check for sub-parts and combine them for the audit
        if not en_text and f"{fid}.sub_0" in en_fns:
            parts = []
            idx = 0
            while f"{fid}.sub_{idx}" in en_fns:
                parts.append(en_fns[f"{fid}.sub_{idx}"])
                idx += 1
            en_text = " ".join(parts)

        poisoned, reason = is_poisoned(en_text, fr_text)
        if poisoned:
            repair_list.append({
                "id": fid,
                "reason": reason,
                "fr_text": fr_text
            })

    print(f"Audit Complete. Found {len(repair_list)} poisoned footnotes.")
    with open("repair_list.json", "w", encoding="utf-8") as f:
        json.dump(repair_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
