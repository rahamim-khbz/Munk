
import json
from robust_parser import extract_and_flatten_robust

def test_on_chapter2():
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Target Chapter 2
    chapter2 = {"text": {"Part 1": {"": {"1": data["text"]["Part 1"][""][1]}}}}
    
    flat, fns = extract_and_flatten_robust(chapter2)
    
    # Check segment 4 (which is index 4 in Chapter 2, part of root.text.Part 1..1.4)
    # The actual path depends on how extract_and_flatten_robust builds it.
    # In my script it was root.text.Part 1.Chapter 2.4
    
    for path, val in flat.items():
        if ".4" in path:
            print(f"--- PATH: {path} ---")
            print(f"TEXT: {val['text'][:500]}...")
            print(f"NUMBER OF FN MARKERS: {val['text'].count('[[fn:')}")
            
    print(f"\nTOTAL FOOTNOTES EXTRACTED: {len(fns)}")

if __name__ == "__main__":
    test_on_chapter2()
