import fitz  # PyMuPDF
import re
import json

def extract_preface_pymupdf():
    doc = fitz.open("Munk's Introduction.pdf")
    
    text_blocks = []
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        
        # Sort blocks vertically, then horizontally if needed
        blocks.sort(key=lambda b: (b[1], b[0]))
        
        for block in blocks:
            # block[4] is the text
            text = block[4].strip()
            if text:
                text_blocks.append(text)
                
    # Now process blocks to find PREFACE
    start_idx = -1
    for i, block in enumerate(text_blocks):
        if block.strip() == "PREFACE.":
            start_idx = i
            break
            
    if start_idx == -1:
        print("Could not find PREFACE.")
        return
        
    end_idx = -1
    for i in range(start_idx + 1, len(text_blocks)):
        if "INTRODUCTION." in block and "Lettre de l'auteur a son disciple." in block:
            end_idx = i
            break
        # Sometimes block split it
        if text_blocks[i].strip() == "INTRODUCTION.":
            if i + 1 < len(text_blocks) and "Lettre de l'auteur a son disciple" in text_blocks[i+1]:
                end_idx = i
                break
            
    if end_idx == -1:
        # Fallback if INTRODUCTION isn't perfectly matched
        print("Could not find end, using fallback search.")
        for i in range(start_idx + 1, len(text_blocks)):
            if "INTRODUCTION" in text_blocks[i]:
                end_idx = i
                break

    if end_idx == -1:
        end_idx = start_idx + 100 # Safety limit
                
    preface_blocks = text_blocks[start_idx+1:end_idx]
    
    paragraphs = []
    
    for block in preface_blocks:
        cleaned = block.replace('\n', ' ').strip()
        
        # Skip roman numeral page numbers
        if re.match(r'^[ivx]+j?$', cleaned.lower()):
            continue
            
        # Skip small junk blocks
        if len(cleaned) < 3 and cleaned.lower() not in ['a', 'y']:
            continue
            
        # skip header
        if cleaned == "PREFACE.":
            continue
            
        paragraphs.append(cleaned)
        
    print(f"Extracted {len(paragraphs)} paragraphs.")
    for i, p in enumerate(paragraphs[:5]):
        print(f"Para {i+1}: {p}")
        
    with open("preface_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_preface_pymupdf()
