
import json
import os
import re

def identify_latin_only(text):
    if not text: return False
    clean = re.sub(r'\[Lat\.:.*?\]', '', text)
    clean = re.sub(r'\[\[.*?\]\]', '', clean)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = clean.strip()
    return len(clean) < 5 and "[Lat.:" in text

def generate_latin_html():
    print("=== Generating Latin Usage HTML Report ===")
    
    # 1. Load Data
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)
    with open("checkpoint_main_text_groq.json", "r") as f:
        english_main = json.load(f)
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        english_fns = json.load(f)

    from munk_pipeline_groq import extract_and_flatten
    flat_fr_main, flat_fr_fns = extract_and_flatten(french_data)
    
    all_en = {**english_main, **english_fns}
    flat_fr = {**flat_fr_main, **flat_fr_fns}
    
    latin_only_count = 0
    results = []
    
    for seg_id, en_text in all_en.items():
        if "[Lat.:" in en_text or "Latin" in en_text:
            fr_text = flat_fr.get(seg_id, {}).get("text", "N/A")
            is_only = identify_latin_only(en_text)
            if is_only: latin_only_count += 1
            
            results.append({
                "id": seg_id,
                "en": en_text,
                "fr": fr_text,
                "type": "Latin-Only" if is_only else "Mixed"
            })

    # 2. Build HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Munk Latin Usage Audit</title>
        <style>
            body {{ font-family: 'Inter', system-ui, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; }}
            .stats {{ background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #334155; }}
            .row {{ display: grid; grid-template-columns: 100px 1fr 1fr; gap: 20px; background: #1e293b; margin-bottom: 10px; padding: 15px; border-radius: 8px; border: 1px solid #334155; }}
            .row.latin-only {{ border-left: 4px solid #ef4444; }}
            .id {{ font-size: 0.8rem; color: #94a3b8; font-family: monospace; }}
            .label {{ font-weight: bold; color: #38bdf8; margin-bottom: 5px; }}
            .text {{ line-height: 1.6; font-size: 0.95rem; }}
            .latin-highlight {{ background: rgba(56, 189, 248, 0.2); border-radius: 4px; padding: 0 4px; }}
            .tag {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; margin-bottom: 10px; }}
            .tag.latin-only {{ background: #ef4444; color: white; }}
            .tag.mixed {{ background: #10b981; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Munk Guide: Latin Usage Audit</h1>
            <div class="stats">
                <p><strong>Total Latin-related segments:</strong> {len(results)}</p>
                <p><strong>Latin-only (Gaps):</strong> <span style="color: #ef4444;">{latin_only_count}</span></p>
                <p><strong>Mixed Usage:</strong> {len(results) - latin_only_count}</p>
            </div>
            
            <div class="header-row row" style="background: transparent; font-weight: bold; border: none;">
                <div>ID</div>
                <div>English Translation</div>
                <div>French Original</div>
            </div>
    """
    
    for r in results:
        # Highlight [Lat.: ...]
        en_h = re.sub(r'(\[Lat\.:.*?\])', r'<span class="latin-highlight">\1</span>', r['en'])
        
        html += f"""
            <div class="row {'latin-only' if r['type'] == 'Latin-Only' else ''}">
                <div class="id">{r['id']}</div>
                <div class="column">
                    <span class="tag {r['type'].lower()}">{r['type']}</span>
                    <div class="text">{en_h}</div>
                </div>
                <div class="column">
                    <div class="label">French Original</div>
                    <div class="text">{r['fr']}</div>
                </div>
            </div>
        """
        
    html += """
        </div>
    </body>
    </html>
    """
    
    with open("latin_usage_report.html", "w") as f:
        f.write(html)
    
    print(f"  [Success] HTML report generated: latin_usage_report.html")
    print(f"  [Stats] Latin-Only: {latin_only_count}, Mixed: {len(results) - latin_only_count}")

if __name__ == "__main__":
    generate_latin_html()
