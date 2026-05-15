import os
import re
import json

def word_count(text):
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'fn\.\d+', ' ', clean_text)
    clean_text = re.sub(r'[^\w\s]', '', clean_text)
    return len(clean_text.split())

def inspect_html_files(directory="viewer"):
    if not os.path.exists(directory):
        if os.path.exists("viewer"):
            directory = "viewer"
        else:
            directory = "."

    html_files = sorted([f for f in os.listdir(directory) if f.endswith('.html')])
    
    total_files = 0
    total_rows = 0
    issues = []
    chapter_summaries = {}

    for filename in html_files:
        # Skip fulltext.html and index.html to avoid duplicate reporting
        if filename in ["fulltext.html", "index.html"]:
            continue
            
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        total_files += 1
        file_issues = []
        
        # Split by parallel-row
        rows = content.split('<div class="parallel-row')
        for i, row_remainder in enumerate(rows[1:]):
            total_rows += 1
            
            # Check if it's a header row (intended empty English cell)
            is_header_row = row_remainder.startswith(' header-row"') or 'class="parallel-row header-row"' in ('<div class="parallel-row' + row_remainder[:50])
            
            he_match = re.search(r'<div class="he-cell">(.*?)</div>', row_remainder, re.DOTALL)
            fr_match = re.search(r'<div class="fr-cell">(.*?)</div>', row_remainder, re.DOTALL)
            en_match = re.search(r'<div class="en-cell">(.*?)</div>', row_remainder, re.DOTALL)
            
            id_match = re.search(r'id="([^"]+)"', row_remainder)
            row_id = id_match.group(1) if id_match else f"row_{i+1}"
            
            en_text = en_match.group(1).strip() if en_match else ""
            he_text = he_match.group(1).strip() if he_match else ""
            fr_text = fr_match.group(1).strip() if fr_match else ""
            
            en_wc = word_count(en_text)
            source_wc = 0
            source_lang = "None"
            
            if he_text:
                source_wc = word_count(he_text)
                source_lang = "he"
            elif fr_text:
                source_wc = word_count(fr_text)
                source_lang = "fr"
                
            issue_types = []
            
            if "[Translation Missing]" in en_text:
                issue_types.append("Missing Translation")
                
            # If not a header row, check for empty text or severe alignment ratios
            if not is_header_row:
                if source_wc > 0:
                    # If source text is just a short bold title, don't strictly enforce ratio if EN is also short/empty
                    is_short_title = source_wc <= 4 and ('<b>' in he_text or '<strong>' in he_text)
                    
                    if not en_text.strip():
                        issue_types.append("Empty EN text")
                    else:
                        ratio = en_wc / source_wc
                        if ratio < 0.3 and source_wc > 6:
                            issue_types.append(f"Low EN word count (Ratio {ratio:.2f})")
                        elif ratio > 3.0 and source_wc > 12:
                            issue_types.append(f"High EN word count (Ratio {ratio:.2f})")
                elif en_wc > 0:
                    issue_types.append("EN text present without Source text")
            else:
                # It's a header row. If it somehow has EN text, that's weird but usually they don't.
                pass

            if issue_types:
                iss_data = {
                    "row_id": row_id,
                    "issues": issue_types,
                    "en_wc": en_wc,
                    "source_wc": source_wc,
                    "source_lang": source_lang,
                    "source_snippet": (he_text or fr_text)[:80].replace('\n', ' ').strip(),
                    "en_snippet": en_text[:80].replace('\n', ' ').strip()
                }
                file_issues.append(iss_data)
                issues.append(dict(iss_data, file=filename))
                
        if file_issues:
            chapter_summaries[filename] = file_issues

    # Generate Markdown Artifact Report
    md_report = "# Translation Alignment & Word Count Inspection Report\n\n"
    md_report += f"**Total Files Scanned:** {total_files} chapters/sections\n"
    md_report += f"**Total Parallel Rows Scanned:** {total_rows}\n"
    md_report += f"**Total Rows with Flagged Issues:** {len(issues)}\n\n"
    
    md_report += "## Summary of Issues by Chapter\n\n"
    for filename, f_issues in chapter_summaries.items():
        md_report += f"### {filename} ({len(f_issues)} issues)\n"
        md_report += "| Row ID | Issues | Source Lang | Source Words | EN Words | Source Snippet | EN Snippet |\n"
        md_report += "|---|---|---|---|---|---|---|\n"
        for iss in f_issues:
            issues_str = ", ".join(iss['issues'])
            src_snip = iss['source_snippet'].replace('|', '&#124;')
            en_snip = iss['en_snippet'].replace('|', '&#124;')
            md_report += f"| `{iss['row_id']}` | {issues_str} | {iss['source_lang']} | {iss['source_wc']} | {iss['en_wc']} | {src_snip} | {en_snip} |\n"
        md_report += "\n"
        
    # Write artifact
    artifact_path = "translation_alignment_report.md"
    # To write an artifact file properly using write_to_file with IsArtifact=True, TargetFile should be the filename.
    # Let's save the markdown string to the artifact.
    # Wait, the tool write_to_file writes to the workspace if TargetFile is an absolute path or relative path.
    # Let's output a summary to stdout when the script runs, and let the script write a markdown report file in the workspace.
    
    with open("alignment_report.md", "w", encoding="utf-8") as f:
        f.write(md_report)
        
    print(f"Inspection complete.")
    print(f"Scanned {total_files} files, {total_rows} total rows.")
    print(f"Found {len(issues)} rows with potential alignment/word count issues.")
    print(f"Detailed markdown report written to 'alignment_report.md'.")
    
    # Print top 5 chapters with most issues
    counts = sorted([(fn, len(iss)) for fn, iss in chapter_summaries.items()], key=lambda x: x[1], reverse=True)
    print("\nChapters with most alignment issues:")
    for fn, count in counts[:10]:
        print(f" - {fn}: {count} issues")

if __name__ == '__main__':
    inspect_html_files()
