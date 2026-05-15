import json
import os

def extract_maqbili_subset():
    # Paths
    munk_path = "/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide/test_translations_threaded.json"
    maqbili_path = "/Users/rayhabbaz/Downloads/Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json"
    output_path = "maqbili_hebrew_subset.json"

    if not os.path.exists(munk_path):
        print(f"Error: Munk JSON not found at {munk_path}")
        return
    if not os.path.exists(maqbili_path):
        print(f"Error: Maqbili JSON not found at {maqbili_path}")
        return

    with open(munk_path, 'r', encoding='utf-8') as f:
        munk_data = json.load(f)
    
    with open(maqbili_path, 'r', encoding='utf-8') as f:
        maqbili_data = json.load(f)

    munk_segments = munk_data.get('segments', {})
    maqbili_text = maqbili_data.get('text', {})

    aligned_maqbili = {}

    # Letter to R Joseph son of Judah (4 segments in Munk)
    letter_refs = [f"Guide_for_the_Perplexed_Letter_to_R_Joseph_son_of_Judah.{i}" for i in range(1, 5)]
    maqbili_letter = maqbili_text.get('Letter to R Joseph son of Judah', [])
    
    if len(maqbili_letter) >= 4:
        # Munk 1: Poem + "In the name of the Lord"
        # In Maqbili[0], the last line is "בשם יי אל עולם".
        aligned_maqbili[letter_refs[0]] = maqbili_letter[0]
        
        # Maqbili[2] contains <sup>1</sup> and <sup>2</sup>.
        # Munk 2 is <sup>1</sup>, Munk 3 is <sup>2</sup>?
        # Actually, let's split Maqbili[2] by "<sup>2</sup>".
        if "<sup>2</sup>" in maqbili_letter[2]:
            parts = maqbili_letter[2].split("<sup>2</sup>")
            aligned_maqbili[letter_refs[1]] = parts[0].strip()
            aligned_maqbili[letter_refs[2]] = "<sup>2</sup>" + parts[1].strip()
        else:
            # Fallback
            aligned_maqbili[letter_refs[1]] = maqbili_letter[2]
            aligned_maqbili[letter_refs[2]] = ""
            
        # Munk 4: "And when God decreed..."
        aligned_maqbili[letter_refs[3]] = maqbili_letter[3]

    # Prefatory Remarks (28 segments in Munk)
    prefatory_refs = [f"Guide_for_the_Perplexed_Prefatory_Remarks.{i}" for i in range(1, 29)]
    maqbili_prefatory = maqbili_text.get('Prefatory Remarks', [])
    
    # 1-to-1 mapping seems to hold for Prefatory Remarks
    for i, ref in enumerate(prefatory_refs):
        if i < len(maqbili_prefatory):
            aligned_maqbili[ref] = maqbili_prefatory[i]

    # Structure the output
    output_data = {
        "metadata": {
            "source": "Maqbili Edition, Mif'al Mishneh Torah, 2024",
            "language": "he",
            "direction": "rtl"
        },
        "segments": aligned_maqbili
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully extracted {len(aligned_maqbili)} Maqbili segments to {output_path}")

if __name__ == "__main__":
    extract_maqbili_subset()
