import json

with open('munk_translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Part 1 Ch 21 Paragraph 4
try:
    ref = 'Guide_for_the_Perplexed_Part_1.21.4'
    trans = data['segments'][ref]
    print("--- Part 1 Ch 21 Segment 4 in MUNK TRANSLATION ---")
    print(f"Word count via split: {len(trans['english'].split())}")
    print(f"Full text:\n{trans['english']}")
except Exception as e:
    print(f"Error finding segment: {e}")
