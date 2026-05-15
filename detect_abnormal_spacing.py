import json
import re

def get_word_count(text):
    if not text:
        return 0
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Strip footnote markers
    text = re.sub(r'\[\[fn:\d+\]\]', '', text)
    text = re.sub(r'\[\[t:\d+\]\]', '', text)
    # Count words
    return len(text.split())

def main():
    print("Loading datasets...")
    try:
        with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
            hebrew_data = json.load(f)
        
        with open("checkpoint_main_text_groq.json", "r") as f:
            english_main = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Configuration for anomaly detection
    # Ratio bounds: English to Hebrew word count
    MIN_RATIO = 0.4
    MAX_RATIO = 3.5
    MIN_WORDS_TO_FLAG = 15  # Don't flag very short segments (like chapter headers)

    anomalies = []
    
    parts = ["Part 1", "Part 2", "Part 3"]
    for part in parts:
        if part not in hebrew_data["text"]: continue
        
        chapters = hebrew_data["text"][part][""]
        for ch_idx, segments in enumerate(chapters):
            ch_num = ch_idx + 1
            # Skip Introduction elements, they are handled differently, but we can check them too
            if isinstance(segments, list):
                for seg_idx, he_text in enumerate(segments):
                    key = f"root.text.{part}..{ch_idx}.{seg_idx}"
                    en_text = ""
                    if key in english_main:
                        en_text = english_main[key]
                    else:
                        sub_idx = 0
                        while f"{key}.sub_{sub_idx}" in english_main:
                            en_text += english_main[f"{key}.sub_{sub_idx}"] + " "
                            sub_idx += 1
                        en_text = en_text.strip()
                    
                    if not en_text and he_text:
                        anomalies.append({
                            "location": f"{part} - Chapter {ch_num} - Seg {seg_idx}",
                            "issue": "Missing English translation",
                            "he_words": get_word_count(he_text),
                            "en_words": 0
                        })
                        continue

                    he_words = get_word_count(he_text)
                    en_words = get_word_count(en_text)
                    
                    if he_words < MIN_WORDS_TO_FLAG and en_words < MIN_WORDS_TO_FLAG:
                        continue
                        
                    ratio = en_words / max(1, he_words)
                    
                    if ratio < MIN_RATIO or ratio > MAX_RATIO:
                        anomalies.append({
                            "location": f"{part} - Chapter {ch_num} - Seg {seg_idx}",
                            "issue": f"Abnormal length ratio: {ratio:.2f} (En/He)",
                            "he_words": he_words,
                            "en_words": en_words,
                            "he_preview": he_text[:50] + "...",
                            "en_preview": en_text[:50] + "..."
                        })

    print(f"Found {len(anomalies)} potentially misaligned segments.")
    if anomalies:
        print("\n--- Anomaly Report ---")
        for a in anomalies:
            print(f"\nLocation: {a['location']}")
            print(f"Issue:    {a['issue']}")
            print(f"Words:    Hebrew: {a['he_words']} | English: {a['en_words']}")
            if "he_preview" in a:
                print(f"He Text:  {a['he_preview']}")
                print(f"En Text:  {a['en_preview']}")
                
        # Write report to file
        report_path = "abnormal_spacing_report.txt"
        with open(report_path, "w") as f:
            f.write("Munk Viewer - Abnormal Spacing / Alignment Report\n")
            f.write("="*50 + "\n\n")
            for a in anomalies:
                f.write(f"Location: {a['location']}\n")
                f.write(f"Issue:    {a['issue']}\n")
                f.write(f"Words:    Hebrew: {a['he_words']} | English: {a['en_words']}\n")
                if "he_preview" in a:
                    f.write(f"He Text:  {a['he_preview']}\n")
                    f.write(f"En Text:  {a['en_preview']}\n")
                f.write("-" * 40 + "\n")
        print(f"\nDetailed report saved to {report_path}")

if __name__ == "__main__":
    main()
