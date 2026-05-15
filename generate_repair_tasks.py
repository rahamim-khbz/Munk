
import json
import re
import os

# CONFIG
FRENCH_JSON = "French_Arabic_Enriched.json"
TRANSLATED_FN_JSON = "checkpoint_footnotes_gemini.json"
MAIN_TEXT_JSON = "checkpoint_main_text_groq.json"

def count_words(text):
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\[\[fn:\d+\]\]', '', clean)
    clean = re.sub(r'\[\[t:\d+\]\]', '', clean)
    return len(clean.split())

def find_balanced_tag(text, start_index):
    match = re.search(r'<i class="footnote">', text[start_index:])
    if not match: return None, None
    content_start = start_index + match.end()
    stack = 1
    curr = content_start
    while stack > 0 and curr < len(text):
        if text.startswith('<i>', curr) or text.startswith('<i ', curr): stack += 1; curr += 3
        elif text.startswith('</i>', curr):
            stack -= 1
            if stack == 0: return text[content_start:curr], curr + 4
            curr += 4
        else: curr += 1
    return None, None

def extract_all_original_footnotes(data):
    flattened_text = {}
    footnotes = {}
    fn_counter = [0]
    def walk(node, current_path):
        if isinstance(node, dict):
            for k, v in node.items(): walk(v, f"{current_path}.{k}")
        elif isinstance(node, list):
            for i, item in enumerate(node): walk(item, f"{current_path}.{i}")
        elif isinstance(node, str):
            text = node
            pos = 0
            processed_text = ""
            marker_pattern = r'<sup class="footnote-marker">\(\d+\)</sup>\s*<i class="footnote">|<i class="footnote">'
            fns_in_this_segment = []
            while True:
                match = re.search(marker_pattern, text[pos:])
                if not match:
                    processed_text += text[pos:]
                    break
                processed_text += text[pos:pos+match.start()]
                content, end_pos = find_balanced_tag(text, pos + match.start())
                if content is not None:
                    id_str = f"fn.{fn_counter[0]}"
                    footnotes[id_str] = {"text": content, "path": current_path}
                    fns_in_this_segment.append(id_str)
                    processed_text += f"[[fn:{fn_counter[0]}]]"
                    fn_counter[0] += 1
                    pos = end_pos
                else:
                    processed_text += text[pos + match.start() : pos + match.end()]
                    pos += match.end()
            flattened_text[current_path] = {"text": processed_text, "fn_ids": fns_in_this_segment}
    walk(data.get("text", {}), "root.text")
    return flattened_text, footnotes

def generate_tasks():
    print("Loading data...")
    with open(FRENCH_JSON, 'r') as f: french_data = json.load(f)
    with open(TRANSLATED_FN_JSON, 'r') as f: trans_fns = json.load(f)
    with open(MAIN_TEXT_JSON, 'r') as f: main_trans = json.load(f)
    
    flat_french, orig_fns = extract_all_original_footnotes(french_data)
    
    tasks = {
        "missing_footnotes": [],
        "poison_footnotes": [],
        "mismatched_segments": [],
        "sequence_gaps": []
    }
    
    # 1. Missing IDs
    for fn_id in orig_fns:
        if fn_id not in trans_fns:
            if not any(k.startswith(f"{fn_id}.sub_") for k in trans_fns):
                tasks["missing_footnotes"].append({"id": fn_id, "text": orig_fns[fn_id]["text"]})
                
    # 2. Poison / Truncated
    for fn_id, orig_info in orig_fns.items():
        orig_words = count_words(orig_info["text"])
        trans_text = ""
        if fn_id in trans_fns: trans_text = trans_fns[fn_id]
        else:
            parts = sorted([k for k in trans_fns if k.startswith(f"{fn_id}.sub_")], 
                           key=lambda x: int(x.split(".sub_")[1]) if ".sub_" in x else 0)
            if parts: trans_text = " ".join([trans_fns[p] for p in parts])
        
        if trans_text:
            trans_words = count_words(trans_text)
            ratio = trans_words / orig_words if orig_words > 0 else 1
            if ratio < 0.5 or ratio > 2.0:
                tasks["poison_footnotes"].append({"id": fn_id, "ratio": ratio, "text": orig_info["text"]})

    # 3. Mismatched Segments (Lost Markers)
    for path, orig_entry in flat_french.items():
        orig_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', orig_entry["text"]))
        if path in main_trans:
            trans_text = main_trans[path] if isinstance(main_trans[path], str) else main_trans[path].get("text", "")
            trans_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', trans_text))
            if orig_fn_count != trans_fn_count:
                tasks["mismatched_segments"].append({"path": path, "orig_text": orig_entry["text"]})

    # 4. Gaps
    sub_bases = set(k.split(".sub_")[0] for k in trans_fns if ".sub_" in k)
    for base in sub_bases:
        idxs = sorted([int(k.split(".sub_")[1]) for k in trans_fns if k.startswith(f"{base}.sub_")])
        if idxs[0] != 0 or any(idxs[i+1] != idxs[i] + 1 for i in range(len(idxs)-1)):
            tasks["sequence_gaps"].append({"id": base, "text": orig_fns[base]["text"]})

    with open("repair_tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)
    
    print(f"Generated repair_tasks.json with:")
    print(f"- {len(tasks['missing_footnotes'])} missing footnotes")
    print(f"- {len(tasks['poison_footnotes'])} poison footnotes")
    print(f"- {len(tasks['mismatched_segments'])} mismatched segments")
    print(f"- {len(tasks['sequence_gaps'])} sequence gaps")

if __name__ == "__main__":
    generate_tasks()
