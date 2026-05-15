import json
import re

with open('French_Healed_Enriched.json', 'r') as f:
    data = json.load(f)

# The segment with the unclosed span
seg = data['text']['Part 2'][''][36][5]

# Fix the specific unclosed span
# Replace '<span dir="rtl"> . Voy. Silv. de Sacy' with '. Voy. Silv. de Sacy'
fixed_seg = seg.replace('<span dir="rtl"> . Voy. Silv. de Sacy', '. Voy. Silv. de Sacy')

data['text']['Part 2'][''][36][5] = fixed_seg

with open('French_Healed_Enriched.json', 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Fixed the unclosed span in root.text.Part 2.[36][5]")
