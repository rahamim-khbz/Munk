import json
with open("checkpoint_main_text_groq.json", "r") as f:
    e = json.load(f)

# Helper to get full text
def get_text(k):
    if k in e: return e[k]
    res = ""
    idx = 0
    while f"{k}.sub_{idx}" in e:
        res += e[f"{k}.sub_{idx}"] + " "
        idx += 1
    return res.strip()

# Helper to set text (handles sub_x cleanup)
def set_text(k, text):
    if k in e:
        e[k] = text
    else:
        # If it was split, we just collapse it back to the main key
        idx = 0
        while f"{k}.sub_{idx}" in e:
            del e[f"{k}.sub_{idx}"]
            idx += 1
        e[k] = text

# 1. Part 1 Ch 56 (idx 55) Seg 3 and 4
en3 = get_text("root.text.Part 1..55.3")
en4 = get_text("root.text.Part 1..55.4")
split_str = "This subject is of great importance"
if split_str in en4:
    parts = en4.split(split_str)
    set_text("root.text.Part 1..55.3", en3 + " " + parts[0].strip())
    set_text("root.text.Part 1..55.4", split_str + parts[1])

# 2. Part 2 Ch 10 (idx 9) Seg 2 and 3
# Let's inspect Seg 2 and 3 for Ch 10 first to ensure we have the right strings
