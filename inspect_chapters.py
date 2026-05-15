import json

chapters_to_inspect = [
    ("Part 1", 55), # Index 55 is Chapter 56
    ("Part 2", 9),  # Index 9 is Chapter 10
    ("Part 2", 10), # Chapter 11
    ("Part 2", 14), # Chapter 15
    ("Part 2", 16), # Chapter 17
    ("Part 2", 17), # Chapter 18
    ("Part 2", 18), # Chapter 19
    ("Part 2", 28), # Chapter 29
    ("Part 3", 18), # Chapter 19
    ("Part 3", 25), # Chapter 26
    ("Part 3", 46)  # Chapter 47
]

with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
    hebrew_data = json.load(f)
with open("checkpoint_main_text_groq.json", "r") as f:
    english_main = json.load(f)

for part, ch_idx in chapters_to_inspect:
    ch_num = ch_idx + 1
    print(f"\n{'='*50}\n{part} - Chapter {ch_num}\n{'='*50}")
    segments = hebrew_data["text"][part][""][ch_idx]
    
    # Also find how many english keys there are for this chapter
    en_keys = [k for k in english_main.keys() if k.startswith(f"root.text.{part}..{ch_idx}.")]
    print(f"Hebrew segments: {len(segments)}")
    
    # We'll just look at the mapping logic
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
            
        he_len = len(he_text.split())
        en_len = len(en_text.split()) if en_text else 0
        ratio = en_len / max(1, he_len)
        print(f"  Seg {seg_idx:2d}: He={he_len:4d} words | En={en_len:4d} words | Ratio={ratio:5.2f}")
        
    # Check if there are trailing english segments
    for k in sorted(en_keys):
        # Extract the segment index
        parts = k.split('.')
        # 'root', 'text', 'Part 1', '', '55', 'X'
        try:
            s_idx = int(parts[-1].split('_')[0] if 'sub' in parts[-1] else parts[-1])
            if s_idx >= len(segments):
                en_text = english_main[k]
                print(f"  EXTRA EN Seg {parts[-1]}: En={len(en_text.split())} words")
        except ValueError:
            pass
