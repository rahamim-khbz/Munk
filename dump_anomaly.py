import json
with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json") as f: h=json.load(f)
with open("checkpoint_main_text_groq.json") as f: e=json.load(f)

def p(part, ch_idx, seg_idx):
    print(f"\n--- {part} Ch {ch_idx+1} Seg {seg_idx} ---")
    print("HE:", h["text"][part][""][ch_idx][seg_idx])
    k = f"root.text.{part}..{ch_idx}.{seg_idx}"
    en_text = ""
    if k in e:
        en_text = e[k]
    else:
        sub_idx = 0
        while f"{k}.sub_{sub_idx}" in e:
            en_text += e[f"{k}.sub_{sub_idx}"] + " "
            sub_idx += 1
        en_text = en_text.strip()
    print("EN:", en_text)

p("Part 2", 10, 2); p("Part 2", 10, 3) # Ch 11
p("Part 2", 14, 2); p("Part 2", 14, 3) # Ch 15
p("Part 2", 16, 4); p("Part 2", 16, 5) # Ch 17
p("Part 2", 17, 1); p("Part 2", 17, 2) # Ch 18
p("Part 2", 18, 15); p("Part 2", 18, 16) # Ch 19
p("Part 2", 28, 23); p("Part 2", 28, 24) # Ch 29
p("Part 3", 18, 1); p("Part 3", 18, 2) # Ch 19
p("Part 3", 25, 1); p("Part 3", 25, 2) # Ch 26
p("Part 3", 46, 2); p("Part 3", 46, 3); p("Part 3", 46, 4) # Ch 47
