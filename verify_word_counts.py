
import json
import re

def count_words(text):
    # Remove markers like [[fn:0]] or [[t:0]] and HTML-like tags
    clean = re.sub(r'\[\[.*?\]\]', '', text)
    clean = re.sub(r'<.*?>', '', clean)
    words = re.findall(r'\w+', clean.lower())
    return len(words)

def main():
    print("--- Munk Translation Fidelity Check (Word Count Ratios) ---")
    
    # 1. Load Checkpoint
    try:
        with open('checkpoint_main_text_groq.json', 'r', encoding='utf-8') as f:
            translated = json.load(f)
    except FileNotFoundError:
        print("Error: checkpoint_main_text_groq.json not found.")
        return

    # 2. Load Source & Flatten (to match keys)
    from munk_pipeline_groq import extract_and_flatten
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        source_data = json.load(f)
    
    flat_source, _ = extract_and_flatten(source_data)
    
    # 3. Compare
    ratios = []
    flags = []
    
    for key, eng_text in translated.items():
        if key not in flat_source:
            continue
            
        fr_text = flat_source[key]["text"]
        
        c_fr = count_words(fr_text)
        c_en = count_words(eng_text)
        
        if c_fr == 0: continue
        
        ratio = c_en / c_fr
        ratios.append(ratio)
        
        # Flagging threshold: < 0.7 or > 1.5
        if ratio < 0.7 or ratio > 1.5:
            flags.append({
                "key": key,
                "fr_words": c_fr,
                "en_words": c_en,
                "ratio": round(ratio, 2),
                "fr_sample": fr_text[:100] + "...",
                "en_sample": eng_text[:100] + "..."
            })

    # 4. Report
    avg_ratio = sum(ratios) / len(ratios) if ratios else 0
    print(f"\nTotal Segments Checked: {len(ratios)}")
    print(f"Average Expansion Ratio: {avg_ratio:.2f}")
    
    if flags:
        print(f"\n🚩 WARNING: {len(flags)} segments flagged for suspicious length ratios:")
        for f in flags:
            print(f"- {f['key']}: Ratio {f['ratio']} (FR: {f['fr_words']} | EN: {f['en_words']})")
            print(f"  FR: {f['fr_sample']}")
            print(f"  EN: {f['en_sample']}\n")
    else:
        print("\n✅ All segments within normal expansion thresholds (0.7 - 1.5).")

if __name__ == "__main__":
    main()
