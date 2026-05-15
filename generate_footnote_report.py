import json
import os
import re

def clean_path(path):
    """Converts a raw data path into a human-readable chapter name."""
    parts = path.split('.')
    if len(parts) < 3: return "Unknown"
    
    # root.text.Part 1.Introduction.0 -> Part 1 Intro
    # root.text.Part 2..1.5 -> Part 2 Ch 2
    # root.text.Letter to R Joseph son of Judah.0 -> Letter
    
    section = parts[2]
    if "Letter" in section: return "Letter to R Joseph"
    if "Prefatory" in section: return "Prefatory Remarks"
    
    if len(parts) >= 5:
        if parts[3] == "Introduction":
            return f"{section} Intro"
        if parts[3] == "": # Chapter index is in parts[4]
            try:
                ch_num = int(parts[4]) + 1
                return f"{section} Ch {ch_num}"
            except:
                return f"{section} Ch {parts[4]}"
    
    return section

def generate_footnote_report():
    source_path = 'French_Arabic_Enriched.json'
    ckpt_path = 'checkpoint_footnotes_gemini.json'
    report_path = 'footnote_status_report.md'
    
    if not os.path.exists(source_path):
        print(f"Source file {source_path} not found.")
        return

    # 1. Load Source and Extract Footnotes
    from munk_pipeline_groq import extract_and_flatten
    with open(source_path, 'r') as f:
        data = json.load(f)
    
    _, flat_footnotes = extract_and_flatten(data)
    total_footnotes = len(flat_footnotes)
    
    # 2. Load Checkpoint
    translated_map = {}
    if os.path.exists(ckpt_path):
        with open(ckpt_path, 'r') as f:
            translated_map = json.load(f)
            
    translated_count = len(translated_map)
            
    # 3. Group by Chapter
    chapters = {}
    for k, v in flat_footnotes.items():
        ch_name = clean_path(v.get('parent_path', 'unknown'))
        if ch_name not in chapters:
            chapters[ch_name] = {'total': 0, 'translated': 0, 'segments': []}
        
        chapters[ch_name]['total'] += 1
        status = "✅ Translated" if k in translated_map else "❌ Missing"
        if k in translated_map:
            chapters[ch_name]['translated'] += 1
        
        chapters[ch_name]['segments'].append({'id': k, 'status': status})

    # 4. Write Report
    with open(report_path, 'w') as f:
        f.write("# Phase 2: Footnote Translation Status Report\n\n")
        
        progress = (translated_count / total_footnotes * 100) if total_footnotes > 0 else 0
        
        f.write(f"**Total Footnotes Found:** {total_footnotes}  \n")
        f.write(f"**Total Translated:** {translated_count}  \n")
        f.write(f"**Progress:** {progress:.1f}%  \n\n")
        
        f.write("## Chapter Summary\n\n")
        f.write("| Chapter | Total | Translated | Status |\n")
        f.write("|---|---|---|---|\n")
        
        # Sort chapters naturally
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        
        for ch_name in sorted(chapters.keys(), key=natural_sort_key):
            stats = chapters[ch_name]
            total = stats['total']
            trans = stats['translated']
            pct = (trans/total*100) if total > 0 else 0
            status = "✅ Complete" if trans == total else f"⏳ {pct:.0f}%"
            f.write(f"| {ch_name} | {total} | {trans} | {status} |\n")

        f.write("\n## Detailed Segment Status\n")
        f.write("Only showing chapters with incomplete translations.\n\n")
        
        for ch_name in sorted(chapters.keys(), key=natural_sort_key):
            stats = chapters[ch_name]
            if stats['translated'] < stats['total']:
                f.write(f"### {ch_name}\n")
                f.write("| Footnote ID | Status |\n")
                f.write("|---|---|\n")
                
                # Sort segments naturally
                sorted_segs = sorted(stats['segments'], key=lambda x: natural_sort_key(x['id']))
                for s in sorted_segs:
                    f.write(f"| `{s['id']}` | {s['status']} |\n")
                f.write("\n")

    print(f"  [Status] Updated {report_path} ({translated_count}/{total_footnotes})")

if __name__ == "__main__":
    generate_footnote_report()
