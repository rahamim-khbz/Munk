
import json
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_TRANS = 'gemini-3-flash-preview'

SYSTEM_PROMPT = '''ROLE AND TASK
You are translating Salomon Munk's French philosophical translation of Maimonides' Guide for the Perplexed into English.
You are translating Munk — not Maimonides. Adopt the register of serious Victorian scholarly prose: formal, precise, somewhat elevated.

MULTILINGUAL CONTENT
- Hebrew/Arabic script: DO NOT TRANSLATE. Preserve these exactly as they appear in the source, including their placement relative to markers.
- Latin: translate into English inline in square brackets [Lat.: ...].
- Greek: preserve in Greek script exactly.

MARKERS (CRITICAL)
- Footnotes: You will see [[fn:0]]. Preserve exactly. DO NOT TRANSLATE.
- HTML Tags: You will see [[t:0]], [[t:1]], etc. DO NOT TRANSLATE.
- RULE: Place these markers in the English translation exactly where the corresponding formatting or footnote should be. They are placeholders for original structure—treat them as immutable symbols.

STRICT OUTPUT FORMAT
Return a JSON object with the EXACT SAME KEYS as the input.
'''

GLOSSARY = ''' TERMINOLOGY GLOSSARY
  intellect          -> intellect
  entendement        -> understanding
  forme              -> form
  matière            -> matter
  faculté            -> faculty
'''

def extract_and_flatten(data, path="root", target_subtree="text"):
    """
    Recursively walks the JSON and extracts translatable strings from the target subtree.
    Excludes metadata outside the target subtree.
    """
    flattened_text = {}
    footnotes = {}
    fn_counter = [0] # Use a list to have a mutable reference in closures

    def walk(node, current_path):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{current_path}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{current_path}.{i}")
        elif isinstance(node, str):
            # 1. Strip footnotes first
            def fn_replacer(match):
                fn_text = match.group(1) or match.group(2)
                
                # Also strip tags from footnote content
                fn_tags = []
                def fn_tag_sub(m):
                    t = m.group(0)
                    tid = len(fn_tags)
                    fn_tags.append(t)
                    return f"[[t:{tid}]]"
                
                fn_text_clean = re.sub(r'<[^>]+>', fn_tag_sub, fn_text)
                
                id_str = f"fn.{fn_counter[0]}"
                footnotes[id_str] = {
                    "text": fn_text_clean,
                    "tags": fn_tags
                }
                
                marker = f"[[fn:{fn_counter[0]}]]"
                fn_counter[0] += 1
                return marker

            fn_pattern = r'<sup class="footnote-marker">\(\d+\)</sup><i class="footnote">(.*?)</i>|<i class="footnote">(.*?)</i>'
            text_no_fns = re.sub(fn_pattern, fn_replacer, node, flags=re.DOTALL)
            
            # 2. Strip HTML tags and replace with [[t:N]] markers
            segment_tags = []
            def tag_replacer(match):
                tag_content = match.group(0)
                tag_id = len(segment_tags)
                segment_tags.append(tag_content)
                return f"[[t:{tag_id}]]"
            
            tag_pattern = r'<[^>]+>'
            processed_text = re.sub(tag_pattern, tag_replacer, text_no_fns)
            
            flattened_text[current_path] = {
                "text": processed_text,
                "tags": segment_tags
            }

    # Only process the target subtree (e.g., 'text')
    if target_subtree in data:
        walk(data[target_subtree], f"{path}.{target_subtree}")
    else:
        # Fallback if the whole object should be flattened
        walk(data, path)

    return flattened_text, footnotes

def chunk_dictionary(flattened_dict, max_chars_per_chunk=5000, max_items_per_chunk=3):
    """
    Groups dictionary items into chunks. 
    Limits to 3 segments OR 5,000 characters, whichever comes first.
    """
    chunks = []
    current_chunk = {}
    current_char_count = 0

    for key, data in flattened_dict.items():
        text = data["text"] if isinstance(data, dict) else data
        item_length = len(str(text)) + len(str(key))

        # Check if adding this item would exceed either limit
        if (current_char_count + item_length > max_chars_per_chunk) or (len(current_chunk) >= max_items_per_chunk):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = {}
            current_char_count = 0

        current_chunk[key] = text
        current_char_count += item_length

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def translate_worker(chunk):
    """
    Translates a chunk. If JSON fails or limit hit, triggers split.
    """
    print(f"    [Working] Starting batch of {len(chunk)} segments...")
    user_msg = f"TRANSLATE THESE SEGMENTS:\n{json.dumps(chunk, ensure_ascii=False, indent=2)}"
    
    for attempt in range(5):
        try:
            res = client.models.generate_content(
                model=MODEL_TRANS,
                contents=user_msg,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT + "\n\n" + GLOSSARY,
                    temperature=0.1 + (attempt * 0.1),
                    response_mime_type='application/json'
                )
            )
            
            raw_text = res.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.split("```", 1)[1].rsplit("```", 1)[0].strip()
            
            # If the response is obviously cut off (no closing brace)
            if not raw_text.endswith("}"):
                raise ValueError("JSON response is unterminated (cut off).")

            parsed = json.loads(raw_text)
            
            if set(parsed.keys()) != set(chunk.keys()):
                print(f"  [Error] Key mismatch. Attempt {attempt+1}...")
                continue
                
            return parsed
            
        except Exception as e:
            print(f"  [Error] Attempt {attempt+1} failed: {str(e)[:100]}")
            
            # If we've failed twice or hit a hard cut-off, try splitting immediately
            if attempt >= 1 and len(chunk) > 1:
                print(f"  [Early Fallback] Splitting chunk of {len(chunk)} due to repeated errors.")
                items = list(chunk.items())
                mid = len(items) // 2
                r1 = translate_worker(dict(items[:mid]))
                r2 = translate_worker(dict(items[mid:]))
                if r1 and r2: return {**r1, **r2}
                return None

            if "429" in str(e):
                time.sleep(10 * (attempt + 1))
            time.sleep(2)
    return None

def inject_translation(data_structure, path_string, translated_text, original_entry):
    """
    Injects a translated string back into the JSON structure based on its path.
    Re-injects the HTML tags stored in the original_entry.
    """
    # 1. Re-inject tags
    final_text = translated_text
    if isinstance(original_entry, dict) and "tags" in original_entry:
        for i, tag in enumerate(original_entry["tags"]):
            final_text = final_text.replace(f"[[t:{i}]]", tag)
            
    keys = path_string.split('.')[1:] # Remove "root"
    current = data_structure
    
    # Navigate to the second-to-last key
    for key in keys[:-1]:
        if key.isdigit(): # It's a list index
            current = current[int(key)]
        else: # It's a dict key
            current = current[key]
            
    # Set the value on the final key
    final_key = keys[-1]
    if final_key.isdigit():
        current[int(final_key)] = final_text
    else:
        current[final_key] = final_text

def run_track(flattened_dict, track_name):
    """
    Processes a track with live checkpointing and heartbeats.
    """
    print(f"\n=== Starting {track_name} Track ===")
    checkpoint_file = f"checkpoint_{track_name.lower().replace(' ', '_')}.json"
    
    # Load existing progress
    translated_map = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            translated_map = json.load(f)
        print(f"  [Resuming] Found {len(translated_map)} items already translated.")
    
    # Filter out items already in checkpoint, preserving original order
    todo_keys = [k for k in flattened_dict.keys() if k not in translated_map]
    todo_items = {k: flattened_dict[k] for k in todo_keys}
    
    if not todo_items:
        print(f"  All items in {track_name} already translated.")
        return translated_map

    # Re-enable chunking with the new 3-segment / 5000-char limits
    chunks = chunk_dictionary(todo_items)
    print(f"  Processing {len(todo_items)} new items in {len(chunks)} batches (max 3 segments each).")

    completed_count = 0
    # Linear processing of these small batches for maximum stability
    print(f"  [Status] Starting linear processing of {len(chunks)} batches...")
    
    for i, chunk in enumerate(chunks):
        # Extract chapter name for logging
        first_path = list(chunk.keys())[0]
        parts = first_path.split('.')
        ch_name = ".".join(parts[2:-1]) if len(parts) > 3 else (parts[2] if len(parts) > 2 else "Unknown")
        if not ch_name or ch_name == "": ch_name = "Main Text"
        
        res = translate_worker(chunk)
        if res:
            translated_map.update(res)
            completed_count += 1
            
            # HEARTBEAT & STATS
            pct = (completed_count / len(chunks)) * 100
            print(f"  [Heartbeat] {track_name}: {completed_count}/{len(chunks)} batches ({pct:.1f}%) | Chapter: {ch_name} | Items: {len(translated_map)}/{len(flattened_dict)}")
            
            # MID-EXECUTION SAVING
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(translated_map, f, ensure_ascii=False, indent=2)
            
            # UPDATE STATUS REPORT (Main Text Track only)
            if track_name == "Main Text":
                update_status_report(flattened_dict, translated_map)
                
            # Rate limit breathing room
            time.sleep(1.0)
        else:
            print(f"  [Warning] Batch {i+1} failed. Skipping to next...")
    
    # Final cleanup: remove checkpoint on full success
    if len(translated_map) == len(flattened_dict):
        # os.remove(checkpoint_file) # Optional: keep it for safety or remove it
        pass
        
    print(f"  {track_name} complete.")
    return translated_map

def update_status_report(flattened_dict, translated_map):
    """
    Generates a markdown status report based on the translated paths.
    """
    REPORT_PATH = "translation_status_report.md"
    
    # Group by chapter (extracting from path e.g. root.text.Part 1 Ch 1.0)
    # We'll assume the path structure matches the JSON tree
    chapters = {}
    
    for path in flattened_dict:
        # Simple heuristic to extract chapter name from path
        parts = path.split('.')
        if len(parts) >= 3:
            # Join parts between 'text' and the final index
            ch_name = ".".join(parts[2:-1]) if len(parts) > 3 else parts[2]
        else:
            ch_name = "Other"
            
        if ch_name not in chapters:
            chapters[ch_name] = {"total": 0, "translated": 0}
        
        chapters[ch_name]["total"] += 1
        if path in translated_map:
            chapters[ch_name]["translated"] += 1
            
    try:
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write("# Translation Status Report (v3)\n\n")
            
            total_segs = len(flattened_dict)
            total_trans = len(translated_map)
            progress = (total_trans / total_segs * 100) if total_segs > 0 else 0
            
            f.write(f"**Total Segments:** {total_segs}  \n")
            f.write(f"**Total Translated:** {total_trans}  \n")
            f.write(f"**Overall Progress:** {progress:.1f}%  \n\n")
            
            f.write("## Chapter Summary\n\n")
            f.write("| Chapter | Total | Translated | Status |\n")
            f.write("|---|---|---|---|\n")
            
            for ch in sorted(chapters.keys()):
                stats = chapters[ch]
                total = stats["total"]
                trans = stats["translated"]
                status = "✅ Complete" if trans == total else f"⏳ {trans}/{total}"
                if trans == 0: status = "⏳ Pending"
                f.write(f"| {ch} | {total} | {trans} | {status} |\n")
                
    except Exception as e:
        print(f"  [Warning] Could not update status report: {e}")

def main():
    import copy
    INPUT_FILE = "French_Arabic_Enriched.json"
    if not os.path.exists(INPUT_FILE):
        INPUT_FILE = "French.json" # Fallback if enrichment hasn't run
        
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
        
    # 1. Flatten
    print("Flattening structure...")
    flat_main, flat_fns = extract_and_flatten(original_data)
    
    # 2. Translate Main
    translated_main = run_track(flat_main, "Main Text")
    
    # 3. Translate Footnotes
    translated_fns = run_track(flat_fns, "Footnotes")
    
    # 4. Reconstruct Main
    print("Reconstructing main text...")
    translated_json = copy.deepcopy(original_data)
    for path, text in translated_main.items():
        original_entry = flat_main.get(path)
        inject_translation(translated_json, path, text, original_entry)
        
    # 5. Save Results
    # Re-inject tags into footnotes before saving
    final_fns = {}
    for fn_id, trans_text in translated_fns.items():
        original_fn = flat_fns.get(fn_id)
        if isinstance(original_fn, dict) and "tags" in original_fn:
            for i, tag in enumerate(original_fn["tags"]):
                trans_text = trans_text.replace(f"[[t:{i}]]", tag)
        final_fns[fn_id] = trans_text

    with open('munk_translations_v3.json', 'w', encoding='utf-8') as f:
        json.dump(translated_json, f, ensure_ascii=False, indent=2)
    
    with open('munk_translated_footnotes_v3.json', 'w', encoding='utf-8') as f:
        json.dump(final_fns, f, ensure_ascii=False, indent=2)
        
    print("DONE. Outputs saved to munk_translations_v3.json and munk_translated_footnotes_v3.json")

if __name__ == "__main__":
    main()
