import re

def clean_preface():
    with open("Munk's Introduction.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Preface starts around line 172
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == "PREFACE.":
            start_idx = i
            break

    # Find the end of the Preface (where INTRODUCTION starts)
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if "INTRODUCTION. Lettre de l'auteur a son disciple." in line:
            end_idx = i
            break

    preface_lines = lines[start_idx:end_idx]
    
    paragraphs = []
    current_para = []

    for line in preface_lines:
        cleaned_line = line.strip()
        
        # Skip empty lines but use them as paragraph breaks
        if not cleaned_line:
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
            continue
            
        # Skip page numbers/headers like "v", "PREFACE.", "ij", etc.
        if cleaned_line == "PREFACE." or re.match(r'^[ivx]+j?$', cleaned_line.lower()):
            continue
        
        # Skip lines that are just single characters like "", ",", "'", "-", etc.
        if len(cleaned_line) <= 1 and cleaned_line not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸàâäçéèêëîïôöùûüÿ":
            continue

        # Skip headers like "PREFACE." with a dot
        if cleaned_line == "PREFACE.":
            continue
            
        current_para.append(cleaned_line)

    if current_para:
        paragraphs.append(" ".join(current_para))

    # Print first few paragraphs
    for i, p in enumerate(paragraphs[:5]):
        print(f"Para {i+1}: {p}\n")
        
    print(f"Total paragraphs extracted: {len(paragraphs)}")
    
    # Save the cleaned paragraphs to a JSON file for processing
    import json
    with open("preface_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    clean_preface()
