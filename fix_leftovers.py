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

# 1. Part 2 Ch 18 (idx 17) Seg 0, 1, 2
en0 = get_text("root.text.Part 2..17.0")
en1 = get_text("root.text.Part 2..17.1")
en2 = get_text("root.text.Part 2..17.2")

split_str1 = "We have a proof thereof in the <i>Active Intellect</i>"
if split_str1 in en0:
    p0, p1 = en0.split(split_str1, 1)
    set_text("root.text.Part 2..17.0", p0)
    set_text("root.text.Part 2..17.1", split_str1 + p1)
    set_text("root.text.Part 2..17.2", en1 + " " + en2)
else:
    print("Failed to fix Part 2 Ch 18")

# 2. Part 2 Ch 19 (idx 18) Seg 17 & 18
en17 = get_text("root.text.Part 2..18.17")
en18 = get_text("root.text.Part 2..18.18")
split_str2 = "There is not, in my judgment, a greater proof of <i>design</i>"
if split_str2 in en17:
    p17, p18 = en17.split(split_str2, 1)
    set_text("root.text.Part 2..18.17", p17)
    set_text("root.text.Part 2..18.18", split_str2 + p18 + " " + en18)
else:
    print("Failed to fix Part 2 Ch 19")

# 3. Part 2 Ch 29 (idx 28) Seg 22 & 23
en22 = get_text("root.text.Part 2..28.22")
en23 = get_text("root.text.Part 2..28.23")
split_str3 = "Now is the matter clear unto thee"
if split_str3 in en23:
    p22_append, p23 = en23.split(split_str3, 1)
    set_text("root.text.Part 2..28.22", en22 + " " + p22_append)
    set_text("root.text.Part 2..28.23", split_str3 + p23)
else:
    print("Failed to fix Part 2 Ch 29")

with open("checkpoint_main_text_groq.json", "w") as f:
    json.dump(e, f, ensure_ascii=False, indent=2)

print("Leftovers fixed!")
