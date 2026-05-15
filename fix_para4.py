import json

# Fix French
with open("preface_resegmented.json", "r", encoding="utf-8") as f:
    fr_paras = json.load(f)

fr_paras[4] = fr_paras[4].replace("dans la IIP partie", "dans la IIIe partie")
fr_paras[4] = fr_paras[4].replace("deMaïmonide", "de Maïmonide") # Also fixing the missing space

with open("preface_resegmented.json", "w", encoding="utf-8") as f:
    json.dump(fr_paras, f, ensure_ascii=False, indent=2)

# Fix English
with open("preface_english_final.json", "r", encoding="utf-8") as f:
    en_paras = json.load(f)

en_paras[4] = en_paras[4].replace("in the second part", "in the third part")

with open("preface_english_final.json", "w", encoding="utf-8") as f:
    json.dump(en_paras, f, ensure_ascii=False, indent=2)

print("Corrections applied to Paragraph 4.")
