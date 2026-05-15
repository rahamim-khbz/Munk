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
        if "INTRODUCTION" in text_blocks[i]:
            end_idx = i
            break
                
    preface_blocks = text_blocks[start_idx+1:end_idx]
    
    paragraphs = []
    current_para = []
    
    for block in preface_blocks:
        cleaned = block.replace('\n', ' ').strip()
        
        # Skip roman numeral page numbers
        if re.match(r'^[ivx]+j?$', cleaned.lower()):
            continue
            
        if cleaned == "PREFACE.":
            continue
            
        # If it's a short line, it might be a page number or header
        if len(cleaned) < 5 and not cleaned.endswith('.'):
            continue
            
        current_para.append(cleaned)
        
        # If the block ends with a sentence ender, consider it end of paragraph
        if cleaned.endswith('.') or cleaned.endswith('?') or cleaned.endswith('!') or cleaned.endswith(':'):
            # Also check if the next block starts a new paragraph or if it's just the end of a line
            # PyMuPDF blocks usually group paragraphs together. But if they don't, we can join them.
            pass
            
    # Since blocks were individual lines, let's join them all and then split by some logic,
    # or just rely on the fact that paragraphs usually start with an indent.
    # Actually, PyMuPDF "blocks" usually represent a paragraph. If it returned single lines,
    # the PDF might not have block structure.
    
    # Let's join everything into one big text, and split by '. ' to form somewhat paragraphs,
    # or just translate block by block if they are paragraphs.
    
    # Let's see if we can use PyMuPDF's get_text("text") and split by double newline
    full_text = ""
    for page_num in range(doc.page_count):
        full_text += doc.load_page(page_num).get_text("text") + "\n"
        
    # Find PREFACE.
    start = full_text.find("PREFACE.\n")
    end = full_text.find("INTRODUCTION.\n", start)
    if end == -1:
        end = full_text.find("INTRODUCTION.", start)
        
    preface_text = full_text[start+len("PREFACE.\n"):end]
    
    # Split by double newline to get paragraphs
    raw_paras = preface_text.split("\n\n")
    final_paras = []
    for p in raw_paras:
        cleaned = p.replace('\n', ' ').strip()
        # remove hyphenation
        cleaned = re.sub(r'-\s+', '', cleaned)
        if len(cleaned) > 10 and not re.match(r'^[ivx]+j?$', cleaned.lower()):
            final_paras.append(cleaned)
            
    print(f"Extracted {len(final_paras)} paragraphs using double newline split.")
    for i, p in enumerate(final_paras[:5]):
        print(f"Para {i+1}: {p}")
        
    with open("preface_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(final_paras, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_preface_pymupdf()
