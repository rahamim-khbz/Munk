import os
import re

def word_count(text):
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'[^\w\s]', '', clean)
    return len(clean.split())

def inspect():
    directory = "viewer_sefaria_full"
    if not os.path.exists(directory):
        print(f"Directory {directory} missing.")
        return
        
    files = sorted([f for f in os.listdir(directory) if f.endswith('.html') and f != 'index.html'])
    issues = []
    total_rows = 0
    
    for filename in files:
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            content = f.read()
            
        rows = content.split('<div class="parallel-row')
        for i, row in enumerate(rows[1:]):
            total_rows += 1
            he_match = re.search(r'<div class="he-cell">(.*?)</div>', row, re.DOTALL)
            en_match = re.search(r'<div class="en-cell">(.*?)</div>', row, re.DOTALL)
            
            he_text = he_match.group(1).strip() if he_match else ""
            en_text = en_match.group(1).strip() if en_match else ""
            
            id_match = re.search(r'id="([^"]+)"', row)
            row_id = id_match.group(1) if id_match else f"row_{i+1}"
            
            he_wc = word_count(he_text)
            en_wc = word_count(en_text)
            
            row_issues = []
            if not en_text or "[Translation Missing]" in en_text:
                row_issues.append("Missing Translation")
            elif he_wc > 0:
                ratio = en_wc / he_wc
                if ratio < 0.15 and he_wc > 15:
                    row_issues.append(f"Low Ratio ({ratio:.2f})")
                elif ratio > 5.0 and he_wc > 15:
                    row_issues.append(f"High Ratio ({ratio:.2f})")
                    
            if row_issues:
                issues.append({
                    "file": filename,
                    "row_id": row_id,
                    "issues": row_issues,
                    "he_wc": he_wc,
                    "en_wc": en_wc
                })
                
    report = "# Sefaria Full Corpus Alignment Audit Report\n\n"
    report += f"**Sections audited:** {len(files)}\n"
    report += f"**Total parallel macro-segments scanned:** {total_rows}\n"
    report += f"**Flagged anomalies:** {len(issues)}\n\n"
    
    if not issues:
        report += "### ✅ Full Production Integrity Confirmed\nZero missing translations or critical word count anomalies detected across the entire corpus."
    else:
        report += "| Section File | Row ID | Issues | HE Words | EN Words |\n|---|---|---|---|---|\n"
        for iss in issues:
            report += f"| {iss['file']} | `{iss['row_id']}` | {', '.join(iss['issues'])} | {iss['he_wc']} | {iss['en_wc']} |\n"
            
    with open("alignment_report_sefaria_full.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Audit complete: Scanned {total_rows} macro-segments across {len(files)} files.")
    print(f"Flagged anomalies: {len(issues)}. Detailed findings saved to alignment_report_sefaria_full.md")

if __name__ == "__main__":
    inspect()
