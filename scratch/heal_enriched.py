import json
import re

print("Loading French_Arabic_Enriched.json...")
with open('French_Arabic_Enriched.json', 'r') as f:
    data = json.load(f)

# Locate the corrupted segment
# Based on find_corruption: root.text.Part 2.[36][5]
# which is data['text']['Part 2'][''][36][5]
corrupted_seg = data['text']['Part 2'][''][36][5]

print(f"Original length: {len(corrupted_seg)} chars")

# We want to remove the junk:
# Starts after: [[t:1]]יםכנוא[[t:2]] au mode subjonctif; il faut sous-entendre la conjonction  [[t:3]].
# Ends before: . Voy. Silv. de Sacy, <i>grammaire arabe</i>

# Actually, the junk is a huge block of text.
# Let's try a regex to find the junk block and remove it.
# The junk block starts with "أنA de#" and ends with "critique of Jesuit casuistry.</span>"

healed_seg = re.sub(r'أنA de.*?critique of Jesuit casuistry\.</span>', '', corrupted_seg, flags=re.DOTALL)

print(f"Healed length: {len(healed_seg)} chars")

# Check if it looks better
print(f"Snippet: {healed_seg[max(0, healed_seg.find('subjonctif')-20):healed_seg.find('subjonctif')+100]}...")

# Update the data
data['text']['Part 2'][''][36][5] = healed_seg

# Save as French_Healed_Enriched.json
print("Saving French_Healed_Enriched.json...")
with open('French_Healed_Enriched.json', 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Done.")
