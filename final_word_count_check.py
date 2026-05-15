import json
import re

# Load French paragraphs
with open("preface_resegmented.json", "r", encoding="utf-8") as f:
    fr_paras = json.load(f)

# Load final English paragraphs
with open("preface_english_final.json", "r", encoding="utf-8") as f:
    en_paras = json.load(f)

# Word count check
results = []
for i in range(len(fr_paras)):
    fr_text = fr_paras[i]
    en_text = en_paras[i]
    
    fr_words = len(re.findall(r'\w+', fr_text))
    en_words = len(re.findall(r'\w+', en_text))
    
    ratio = en_words / fr_words if fr_words > 0 else 0
    
    results.append({
        "index": i,
        "fr_count": fr_words,
        "en_count": en_words,
        "ratio": round(ratio, 2)
    })

# Print summary
print(f"{'Para':<5} | {'FR Count':<10} | {'EN Count':<10} | {'Ratio':<10} | {'Status'}")
print("-" * 60)
for r in results:
    status = "OK" if 0.7 <= r["ratio"] <= 1.4 else "WARN"
    print(f"{r['index']:<5} | {r['fr_count']:<10} | {r['en_count']:<10} | {r['ratio']:<10} | {status}")
