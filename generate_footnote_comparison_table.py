
import json
import re

def count_footnotes_in_html(html_list):
    count = 0
    pattern = re.compile(r'class="footnote-marker"')
    for segment in html_list:
        count += len(pattern.findall(segment))
    return count

def count_footnotes_in_english(segments_dict, prefix):
    count = 0
    pattern = re.compile(r'\[\[fn:\d+\]\]')
    for key, text in segments_dict.items():
        if key.startswith(prefix):
            count += len(pattern.findall(text))
    return count

def main():
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)["text"]
    
    with open("checkpoint_main_text_groq.json", "r") as f:
        english_data = json.load(f)

    report = []
    report.append("| Chapter Path | French Footnotes | English Footnotes | Delta |")
    report.append("|---|---|---|---|")

    # Mapping logic
    # Prefatory Remarks -> root.text.Prefatory Remarks
    # Part X -> root.text.Part X
    
    # Simple top-level keys
    for key in ["Introduction of Ibn Tibon", "Letter to R Joseph son of Judah", "Prefatory Remarks"]:
        if key in french_data:
            fr_count = count_footnotes_in_html(french_data[key])
            en_prefix = f"root.text.{key}"
            en_count = count_footnotes_in_english(english_data, en_prefix)
            report.append(f"| {key} | {fr_count} | {en_count} | {en_count - fr_count} |")

    # Parts
    for part_num in [1, 2, 3]:
        part_key = f"Part {part_num}"
        if part_key in french_data:
            # Introduction
            if "Introduction" in french_data[part_key]:
                fr_count = count_footnotes_in_html(french_data[part_key]["Introduction"])
                en_prefix = f"root.text.{part_key}.Introduction"
                en_count = count_footnotes_in_english(english_data, en_prefix)
                report.append(f"| {part_key} Introduction | {fr_count} | {en_count} | {en_count - fr_count} |")
            
            # Chapters
            chapters = french_data[part_key].get("", [])
            for i, chapter_segments in enumerate(chapters):
                fr_count = count_footnotes_in_html(chapter_segments)
                # Map to root.text.Part X..Y
                en_prefix = f"root.text.{part_key}..{i}." # Note the double dot and chapter index
                en_count = count_footnotes_in_english(english_data, en_prefix)
                report.append(f"| {part_key} Chapter {i+1} | {fr_count} | {en_count} | {en_count - fr_count} |")

    print("\n".join(report))

if __name__ == "__main__":
    main()
