
import json
import re
from munk_pipeline_groq import extract_and_flatten

def get_word_count(text):
    if not text: return 0
    # Clean HTML for counting
    clean = re.sub(r'<[^>]*>', '', text)
    return len(re.findall(r'\w+', clean))

def main():
    print("Loading datasets...")
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)
    
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        english_fns = json.load(f)

    print("Extracting original footnotes and mapping to chapters...")
    # extract_and_flatten gives us flat_fns[fid] = {'text': ..., 'path': ...}
    _, flat_fns = extract_and_flatten(french_data)

    # Group word counts by chapter
    # Chapter format: "Part 1..ChapterIndex"
    chapter_stats = {}

    for fid, info in flat_fns.items():
        path = info['parent_path'] # e.g. "root.text.Part 1..2"
        # Extract chapter identifier
        # Part 1..2 -> Part 1 Chapter 3 (since 0-indexed)
        parts = path.split('.')
        chapter_id = "Unknown"
        
        if "Prefatory Remarks" in path:
            chapter_id = "Prefatory Remarks"
        elif "Letter to R Joseph" in path:
            chapter_id = "Letter to Joseph"
        elif "Introduction" in path:
            # root.text.Part 1.Introduction
            chapter_id = f"{parts[2]} Introduction"
        elif len(parts) >= 4 and parts[3].isdigit():
            # root.text.Part 1..36 (Wait, it might be double dot or single dot depending on nesting)
            part_name = parts[2]
            chap_idx = int(parts[3])
            chapter_id = f"{part_name} Chapter {chap_idx + 1}"
        elif len(parts) >= 5 and parts[3] == "" and parts[4].isdigit():
            # root.text.Part 1..36
            part_name = parts[2]
            chap_idx = int(parts[4])
            chapter_id = f"{part_name} Chapter {chap_idx + 1}"
        else:
            chapter_id = ".".join(parts[2:4])

        if chapter_id not in chapter_stats:
            chapter_stats[chapter_id] = {"fr_words": 0, "en_words": 0}
        
        # French count
        fr_text = info['text']
        chapter_stats[chapter_id]["fr_words"] += get_word_count(fr_text)

        # English count (including sub-parts)
        # Check if fid exists or fid.sub_0 etc exists
        if fid in english_fns:
            chapter_stats[chapter_id]["en_words"] += get_word_count(english_fns[fid])
        else:
            # Check for sub-parts
            sub_prefix = f"{fid}.sub_"
            for sub_id, sub_text in english_fns.items():
                if sub_id.startswith(sub_prefix):
                    chapter_stats[chapter_id]["en_words"] += get_word_count(sub_text)

    # Generate Report
    report = []
    report.append("| Chapter | French Footnote Words | English Footnote Words | Delta | Ratio |")
    report.append("|---|---|---|---|---|")

    # Sort chapters logically if possible, or just alphabetically for now
    for chap in sorted(chapter_stats.keys()):
        stats = chapter_stats[chap]
        fr = stats["fr_words"]
        en = stats["en_words"]
        delta = en - fr
        ratio = en / fr if fr > 0 else 0
        report.append(f"| {chap} | {fr} | {en} | {delta} | {ratio:.2f} |")

    with open("footnote_wordcount_breakdown.md", "w") as f:
        f.write("# Footnote Word Count Breakdown by Chapter\n\n")
        f.write("\n".join(report))
    
    print("Report generated: footnote_wordcount_breakdown.md")

if __name__ == "__main__":
    main()
