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

def split_and_move(k_from, k_to, split_str, move_to_start=True):
    text_from = get_text(k_from)
    text_to = get_text(k_to)
    
    if split_str not in text_from:
        print(f"WARNING: '{split_str[:30]}...' not found in {k_from}")
        return
        
    parts = text_from.split(split_str, 1)
    
    if move_to_start:
        # moving the second part to the start of k_to
        set_text(k_from, parts[0])
        set_text(k_to, split_str + parts[1] + " " + text_to)
    else:
        # moving the first part to the end of k_to
        set_text(k_to, text_to + " " + parts[0])
        set_text(k_from, split_str + parts[1])
        
def direct_set(k, text):
    set_text(k, text)

# 1. Part 1 Ch 56 (idx 55) Seg 3 & 4
split_and_move("root.text.Part 1..55.4", "root.text.Part 1..55.3", "This subject is of great importance", move_to_start=False)

# 2. Part 2 Ch 10 (idx 9) Seg 2 & 3
split_and_move("root.text.Part 2..9.2", "root.text.Part 2..9.3", "Likewise, the causes of all movement of the spheres are four in number")

# 3. Part 2 Ch 11 (idx 10) Seg 2 & 3
split_and_move("root.text.Part 2..10.2", "root.text.Part 2..10.3", "But the matter is as I shall state:")

# 4. Part 2 Ch 15 (idx 14) Seg 2 & 3
split_and_move("root.text.Part 2..14.2", "root.text.Part 2..14.3", "Wherefore I have deemed it my duty")

# 5. Part 2 Ch 17 (idx 16) Seg 4 & 5
split_and_move("root.text.Part 2..16.5", "root.text.Part 2..16.4", "Likewise, when he says of circular motion", move_to_start=False)

# 6. Part 2 Ch 18 (idx 17) Seg 0, 1, 2
en0 = get_text("root.text.Part 2..17.0")
en1 = get_text("root.text.Part 2..17.1")
en2 = get_text("root.text.Part 2..17.2")

split_str = "We have a proof thereof in the Active Intellect"
if split_str in en0:
    p0, p1 = en0.split(split_str, 1)
    set_text("root.text.Part 2..17.0", p0)
    set_text("root.text.Part 2..17.1", split_str + p1)
    set_text("root.text.Part 2..17.2", en1 + " " + en2)

# 7. Part 2 Ch 19 (idx 18) Seg 15, 16, 17, 18
en15 = get_text("root.text.Part 2..18.15")
en16 = get_text("root.text.Part 2..18.16")
en17 = get_text("root.text.Part 2..18.17")

split1 = "But, as soon as it is admitted that all is due to the design"
split2 = "and there is no further room for enquiry, unless thou shouldst ask"

if split1 in en15 and split2 in en15:
    p15, rest = en15.split(split1, 1)
    p16, p17_start = rest.split(split2, 1)
    
    set_text("root.text.Part 2..18.15", p15)
    set_text("root.text.Part 2..18.16", split1 + p16)
    set_text("root.text.Part 2..18.17", split2 + p17_start + " " + en16 + " " + en17)
    # Note: En 17 original is actually pushed back, but we'll leave it in 17 for now to avoid breaking Seg 18
    # Actually, we can move the old EN17 to EN18 if we want, but let's just append it to 17.

# 8. Part 2 Ch 29 (idx 28) Seg 23 & 24
split_and_move("root.text.Part 2..28.24", "root.text.Part 2..28.23", "Such is our opinion", move_to_start=False)

# 9. Part 3 Ch 19 (idx 18) Seg 1 & 2
split_and_move("root.text.Part 3..18.1", "root.text.Part 3..18.2", "But a prophet (Asaph) tells us that after having long reflected upon this subject")

# 10. Part 3 Ch 26 (idx 25) Seg 1 & 2
split_and_move("root.text.Part 3..25.2", "root.text.Part 3..25.1", "A more exact example of the particular details is found in the sacrifices", move_to_start=False)

# 11. Part 3 Ch 47 (idx 46) Seg 3 & 4
split_and_move("root.text.Part 3..46.3", "root.text.Part 3..46.4", "In measure as the case of uncleanness might happen more frequently")


with open("checkpoint_main_text_groq.json", "w") as f:
    json.dump(e, f, ensure_ascii=False, indent=2)

print("All anomalies fixed and saved!")
