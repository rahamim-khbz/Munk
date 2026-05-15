import json

with open("checkpoint_main_text_groq.json", "r") as f:
    e = json.load(f)

def get_text(k):
    if k in e: return e[k]
    res = ""
    idx = 0
    while f"{k}.sub_{idx}" in e:
        res += e[f"{k}.sub_{idx}"] + " "
        idx += 1
    return res.strip()

def set_text(k, text):
    if k in e:
        e[k] = text.strip()
    else:
        idx = 0
        while f"{k}.sub_{idx}" in e:
            del e[f"{k}.sub_{idx}"]
            idx += 1
        e[k] = text.strip()

k_from = "root.text.Part 3..25.2"
k_to = "root.text.Part 3..25.1"
split_str = "A more exact example of the <i>particular details</i> is found in the sacrifices"

text_from = get_text(k_from)
text_to = get_text(k_to)

if split_str in text_from:
    parts = text_from.split(split_str, 1)
    # moving the first part to the end of k_to
    set_text(k_to, text_to + " " + parts[0].strip())
    set_text(k_from, split_str + parts[1])
    print("Fixed Part 3 Ch 26!")
else:
    print("Still not found!")

with open("checkpoint_main_text_groq.json", "w") as f:
    json.dump(e, f, ensure_ascii=False, indent=2)
