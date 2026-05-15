import json

with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json") as f: h=json.load(f)
with open("checkpoint_main_text_groq.json") as f: e=json.load(f)

def get_en(k):
    if k in e: return e[k]
    res, idx = "", 0
    while f"{k}.sub_{idx}" in e:
        res += e[f"{k}.sub_{idx}"] + " "
        idx += 1
    return res.strip()

def p(part, ch_idx, segs):
    print(f"\n{'='*40}\n{part} Ch {ch_idx+1}\n{'='*40}")
    for seg_idx in segs:
        k = f"root.text.{part}..{ch_idx}.{seg_idx}"
        print(f"\n--- Seg {seg_idx} ---")
        try:
            print("HE:", h["text"][part][""][ch_idx][seg_idx])
        except IndexError:
            print("HE: [missing]")
        print("EN:", get_en(k))

p("Part 2", 17, [0, 1, 2]) # Ch 18
p("Part 2", 18, [15, 16, 17]) # Ch 19
p("Part 2", 28, [23, 24]) # Ch 29
p("Part 3", 18, [1, 2]) # Ch 19
p("Part 3", 25, [1, 2]) # Ch 26
p("Part 3", 46, [2, 3, 4]) # Ch 47
