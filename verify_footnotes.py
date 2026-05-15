import json
import os
from munk_pipeline_groq import extract_and_flatten

BASE_DIR = '.'
INPUT_FILE = os.path.join(BASE_DIR, 'French_Arabic_Enriched.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'checkpoint_footnotes_rehab_groq.json')
FALLBACK_FILE = os.path.join(BASE_DIR, 'checkpoint_footnotes_gemini.json')

def consolidate_sub_footnotes(raw_fns):
    merged = {}
    sub_groups = {}
    for k, v in raw_fns.items():
        if ".sub_" in k:
            base, idx = k.rsplit(".sub_", 1)
            sub_groups.setdefault(base, []).append((int(idx), v))
        else:
            merged[k] = v
    for base_id, parts in sub_groups.items():
        parts.sort(key=lambda x: x[0])
        merged[base_id] = " ".join(p[1] for p in parts)
    return merged

def run_verification():
    print("=== Footnote Verification (Canonical Sequential Mapping) ===")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    _, fr_fns = extract_and_flatten(data)
    print(f"Extracted {len(fr_fns)} raw footnote chunks from source.")
    
    # Base canonical IDs without .sub_ suffixes
    canonical_fr_ids = sorted(list(set(k.split(".sub_")[0] for k in fr_fns.keys())), key=lambda x: int(x.split('.')[1]))
    print(f"Total unique consolidated base footnotes in source: {len(canonical_fr_ids)}")
    
    results = {}
    if os.path.exists(FALLBACK_FILE):
        with open(FALLBACK_FILE, 'r', encoding='utf-8') as f:
            fallback = json.load(f)
            results.update(consolidate_sub_footnotes(fallback))
            
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            rehab = json.load(f)
            # Rehab file overrides fallback
            results.update(rehab)
            
    print(f"Loaded {len(results)} consolidated translated footnotes.")
    
    missing = []
    flagged = []
    
    for fn_id in canonical_fr_ids:
        if fn_id not in results:
            missing.append(fn_id)
            continue
            
        # Reconstruct full French text by joining sub-parts if any
        sub_keys = sorted([k for k in fr_fns if k.startswith(f"{fn_id}.sub_")], key=lambda x: int(x.split('_')[-1]))
        if sub_keys:
            fr_text = " ".join(fr_fns[sk]['text'] for sk in sub_keys)
        else:
            fr_text = fr_fns.get(fn_id, {}).get('text', '')
            
        en_text = results[fn_id]
        
        fr_words = len(fr_text.split())
        en_words = len(en_text.split())
        
        if fr_words > 0:
            diff_pct = ((en_words - fr_words) / fr_words) * 100
            if diff_pct < -50:
                flagged.append((fn_id, diff_pct, fr_words, en_words))
                
    if missing:
        print(f"\n❌ Missing {len(missing)} footnotes!")
        for m in missing[:10]:
            print(f"  - {m}")
        if len(missing) > 10: print("  ...")
    else:
        print("\n✅ All footnotes translated successfully!")
        
    if flagged:
        print(f"\n⚠️ Flagged {len(flagged)} footnotes for huge word count drop (< -50%):")
        for f in flagged[:20]:
            print(f"  - {f[0]}: {f[1]:.1f}% (Fr:{f[2]} -> En:{f[3]})")
        if len(flagged) > 20: print("  ...")
    else:
        print("\n✅ No massive word count drops detected!")

if __name__ == '__main__':
    run_verification()
