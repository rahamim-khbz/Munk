
import json
import re
import os

def wc(text):
    if not text: return 0
    return len(re.findall(r'\w+', text))

def clean_french(text):
    if not text: return ""
    
    # 1. Remove footnote markers
    text = re.sub(r'<sup class="footnote-marker">.*?</sup>', '', text, flags=re.DOTALL)
    
    # 2. Remove footnote content blocks robustly (handling nested <i> tags)
    while True:
        start_idx = text.find('<i class="footnote">')
        if start_idx == -1:
            break
            
        depth = 0
        current_idx = start_idx
        end_idx = -1
        
        tags = list(re.finditer(r'<(/?i)\b[^>]*>', text[start_idx:]))
        for tag in tags:
            tag_name = tag.group(1)
            if tag_name == 'i':
                depth += 1
            elif tag_name == '/i':
                depth -= 1
            
            if depth == 0:
                end_idx = start_idx + tag.end()
                break
        
        if end_idx != -1:
            text = text[:start_idx] + text[end_idx:]
        else:
            # Fallback
            last_i = text.rfind('</i>')
            if last_i > start_idx:
                text = text[:start_idx] + text[last_i+5:]
            else:
                text = text[:start_idx]
                break
                
    # 3. Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def clean_english(text):
    if not text: return ""
    # Remove structural placeholders
    text = re.sub(r'\[\[t:\d+\]\]', '', text)
    text = re.sub(r'\[\[fn:\d+\]\]', '', text)
    # Remove any stray HTML tags (though EN should be mostly clean of tags except for <i> etc)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def flatten_main(data, prefix='root'):
    result = {}
    if isinstance(data, list):
        for i, item in enumerate(data):
            result.update(flatten_main(item, f'{prefix}.{i}'))
    elif isinstance(data, dict):
        for k, v in data.items():
            result.update(flatten_main(v, f'{prefix}.{k}'))
    elif isinstance(data, str):
        result[prefix] = data
    return result

def main():
    print("Generating Cleaned Audit JSON...")
    
    # Load files
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        fr_data = json.load(f)
    
    with open('checkpoint_main_text_groq.json', 'r', encoding='utf-8') as f:
        en_data = json.load(f)
        
    fr_flat = flatten_main(fr_data)
    fr_main_keys = [k for k in fr_flat.keys() if 'root.text.' in k and '.fn.' not in k and 'footnotes' not in k]
    
    comparison = []
    
    for key in fr_main_keys:
        raw_fr = fr_flat[key]
        raw_en = en_data.get(key, "")
        
        if not raw_en or raw_en == "[Translation Missing]":
            continue
            
        clean_fr = clean_french(raw_fr)
        clean_en = clean_english(raw_en)
        
        fr_wc = wc(clean_fr)
        en_wc = wc(clean_en)
        
        ratio = en_wc / fr_wc if fr_wc > 0 else 0
        dev = abs(ratio - 1.0)
        
        comparison.append({
            "id": key,
            "fr_clean_wc": fr_wc,
            "en_clean_wc": en_wc,
            "ratio": round(ratio, 3),
            "deviation": round(dev, 3),
            "fr_text_preview": clean_fr[:100],
            "en_text_preview": clean_en[:100]
        })
        
    with open('audit_cleaned_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(comparison)} segments to audit_cleaned_comparison.json")
    
    # Rerun summary analysis
    dev_bands = {
        "0-5%": 0,
        "5-10%": 0,
        "10-15%": 0,
        "15-20%": 0,
        "20-25%": 0,
        "25%+" : 0
    }
    
    total_segments = len(comparison)
    for item in comparison:
        d = item["deviation"]
        if d <= 0.05: dev_bands["0-5%"] += 1
        elif d <= 0.10: dev_bands["5-10%"] += 1
        elif d <= 0.15: dev_bands["10-15%"] += 1
        elif d <= 0.20: dev_bands["15-20%"] += 1
        elif d <= 0.25: dev_bands["20-25%"] += 1
        else: dev_bands["25%+"] += 1
        
    print("\n=== CLEANED DEVIATION SUMMARY ===")
    for band, count in dev_bands.items():
        pct = (count / total_segments) * 100
        print(f"{band:<10}: {count:>5} ({pct:>5.1f}%)")
        
    # Show top 5 outliers
    print("\n=== TOP 5 OUTLIERS (Cleaned) ===")
    outliers = sorted(comparison, key=lambda x: x["deviation"], reverse=True)[:5]
    for o in outliers:
        print(f"ID: {o['id']} | Ratio: {o['ratio']} | Dev: {o['deviation']}")
        print(f"  FR: {o['fr_text_preview']}...")
        print(f"  EN: {o['en_text_preview']}...")

if __name__ == "__main__":
    main()
