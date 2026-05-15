import json
import re

# Load French paragraphs
with open("preface_resegmented.json", "r", encoding="utf-8") as f:
    fr_paras = json.load(f)

# Load English segments
with open("checkpoint_main_text_groq.json", "r", encoding="utf-8") as f:
    data = json.load(f)

en_segments = []
for i in range(11):
    key = f"root.text.Munk's Introduction.{i}"
    if key in data:
        en_segments.append(data[key])

# Merge and clean English text
full_en = " ".join(en_segments)
full_en = re.sub(r"\s+", " ", full_en).strip()

# Improved start phrases (English)
en_starts = [
    "The work of Maimonides",
    "As the true founder",
    "But the high reputation",
    "In Egypt, where Maimonides lived",
    "The fame enjoyed by",
    "I must not anticipate here",
    "It will be easily understood",
    "Since Buxtorf, the Guide",
    "For more than twenty years",
    "I announced this project",
    "A journey I made to Oxford",
    "Finding myself finally in possession",
    "The total loss of sight",
    "I must now give the reader",
    "This first volume contains",
    "We have seen what my resources were",
    "However, I have preserved",
    "In the French translation",
    "It is only too easy",
    "I have accompanied the translation",
    "A certain number of critical notes",
    "I cannot conclude this preface",
    "I have had to struggle",
    "The gravity of this mission",
    "S. MUNK."
]

# Find positions of start phrases
positions = []
for phrase in en_starts:
    # Try fuzzy matching (case insensitive, flexible spacing)
    match = re.search(re.escape(phrase), full_en, re.IGNORECASE)
    if match:
        positions.append(match.start())
    else:
        # Try keywords
        keywords = phrase.split()[:3]
        pattern = r"\b" + r"\b.*\b".join(keywords) + r"\b"
        match = re.search(pattern, full_en, re.IGNORECASE)
        if match:
            positions.append(match.start())
        else:
            positions.append(-1)

# Sort positions (they should be in order)
valid_positions = sorted([p for p in positions if p != -1])

# Split into paragraphs
en_paras = []
for i in range(len(positions)):
    pos = positions[i]
    if pos == -1:
        en_paras.append("")
        continue
    
    # Find the next valid position
    next_pos = -1
    for p in valid_positions:
        if p > pos:
            next_pos = p
            break
    
    if next_pos != -1:
        en_paras.append(full_en[pos:next_pos].strip())
    else:
        en_paras.append(full_en[pos:].strip())

# Word count check
results = []
for i in range(len(fr_paras)):
    fr_text = fr_paras[i]
    en_text = en_paras[i] if i < len(en_paras) else ""
    
    fr_words = len(re.findall(r'\w+', fr_text))
    en_words = len(re.findall(r'\w+', en_text))
    
    ratio = en_words / fr_words if fr_words > 0 else 0
    
    results.append({
        "index": i,
        "fr_start": fr_text[:40] + "...",
        "en_start": en_text[:40] + "...",
        "fr_count": fr_words,
        "en_count": en_words,
        "ratio": round(ratio, 2)
    })

# Save results
with open("preface_alignment_check.json", "w", encoding="utf-8") as f:
    json.dump({"comparison": results, "en_paras": en_paras}, f, ensure_ascii=False, indent=2)

# Print summary
print(f"{'Para':<5} | {'FR Count':<10} | {'EN Count':<10} | {'Ratio':<10} | {'Status'}")
print("-" * 60)
for r in results:
    status = "OK" if 0.7 <= r["ratio"] <= 1.6 else "WARN"
    if r["en_count"] == 0: status = "MISSING"
    print(f"{r['index']:<5} | {r['fr_count']:<10} | {r['en_count']:<10} | {r['ratio']:<10} | {status}")
