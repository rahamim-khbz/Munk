
import os
import json
import requests
import time
import re
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get('VITE_GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_TRANS = 'llama-3.3-70b-versatile'

SYSTEM_PROMPT = '''Translate French to English. Adopt a serious Victorian scholarly prose style.
- Preserve Hebrew/Arabic script.
- Translate Latin inline in [Lat.: ...].
- Preserve markers [[fn:N]] and [[t:N]] exactly.
Return ONLY a JSON object with the original keys.
'''

GLOSSARY = ''' TERMINOLOGY GLOSSARY
  intellect          -> intellect
  entendement        -> understanding
  forme              -> form
  matière            -> matter
  faculté            -> faculty
'''

class GroqRateLimiter:
    def __init__(self, tpm_limit=5000, rpm_limit=3):
        self.tpm_limit = tpm_limit
        self.rpm_limit = rpm_limit
        self.history = [] 

    def wait_for_limit(self, estimated_tokens):
        now = time.time()
        self.history = [h for h in self.history if now - h[0] < 60]
        
        current_tpm = sum(h[1] for h in self.history)
        current_rpm = len(self.history)
        
        if current_rpm >= self.rpm_limit:
            sleep_time = 60 - (now - self.history[0][0]) + 0.5
            print(f"  [Rate Limit] RPM limit reached ({current_rpm}). Sleeping {sleep_time:.2f}s...")
            time.sleep(max(0.1, sleep_time))
            return self.wait_for_limit(estimated_tokens)

        if current_tpm + estimated_tokens > self.tpm_limit:
            needed_space = (current_tpm + estimated_tokens) - self.tpm_limit
            acc = 0
            for ts, tokens in self.history:
                acc += tokens
                if acc >= needed_space:
                    sleep_time = 60 - (now - ts) + 0.5
                    print(f"  [Rate Limit] TPM limit approaching ({current_tpm}). Sleeping {sleep_time:.2f}s...")
                    time.sleep(max(0.1, sleep_time))
                    break
        
    def add_usage(self, tokens):
        self.history.append((time.time(), tokens))

rate_limiter = GroqRateLimiter()

def find_balanced_tag(text, start_index):
    match = re.search(r'<i class="footnote">', text[start_index:])
    if not match:
        return None, None
    content_start = start_index + match.end()
    stack = 1
    curr = content_start
    while stack > 0 and curr < len(text):
        if text.startswith('<i>', curr) or text.startswith('<i ', curr):
            stack += 1
            curr += 3
        elif text.startswith('</i>', curr):
            stack -= 1
            if stack == 0:
                return text[content_start:curr], curr + 4
            curr += 4
        else:
            curr += 1
    return None, None

def split_text_intelligently(text, max_len=2500):
    """Splits text into chunks at sentence boundaries."""
    if len(text) <= max_len:
        return [text]
    
    parts = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for p in parts:
        if len(current) + len(p) < max_len:
            current = (current + " " + p).strip()
        else:
            if current: chunks.append(current)
            current = p
    if current: chunks.append(current)
    return chunks

def extract_and_flatten(data, path="root", target_subtree="text"):
    flattened_text = {}
    footnotes = {}
    fn_counter = [0]

    def walk(node, current_path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{current_path}.{k}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{current_path}.{i}")
        elif isinstance(node, str):
            # 1. Extract Footnotes Balanced
            text = node
            pos = 0
            processed_text = ""
            marker_pattern = r'<sup class="footnote-marker">\(\d+\)</sup>\s*<i class="footnote">|<i class="footnote">'
            
            while True:
                match = re.search(marker_pattern, text[pos:])
                if not match:
                    processed_text += text[pos:]
                    break
                processed_text += text[pos:pos+match.start()]
                content, end_pos = find_balanced_tag(text, pos + match.start())
                if content is not None:
                    fn_tags = []
                    def fn_tag_sub(m):
                        t = m.group(0); tid = len(fn_tags); fn_tags.append(t)
                        return f"[[t:{tid}]]"
                    fn_text_clean = re.sub(r'<[^>]+>', fn_tag_sub, content)
                    
                    # Split long footnotes
                    if len(fn_text_clean) > 3000:
                        sub_fns = split_text_intelligently(fn_text_clean)
                        for i, part in enumerate(sub_fns):
                            id_str = f"fn.{fn_counter[0]}.sub_{i}"
                            footnotes[id_str] = {"text": part, "tags": fn_tags, "parent_path": current_path}
                        fn_counter[0] += 1 # Increment main counter
                    else:
                        id_str = f"fn.{fn_counter[0]}"
                        footnotes[id_str] = {"text": fn_text_clean, "tags": fn_tags, "parent_path": current_path}
                        fn_counter[0] += 1
                    
                    processed_text += f"[[fn:{fn_counter[0]-1}]]"
                    pos = end_pos
                else:
                    processed_text += text[pos + match.start() : pos + match.end()]
                    pos += match.end()

            # 2. Extract tags
            segment_tags = []
            def tag_replacer_bulk(match):
                all_tags = re.findall(r'<[^>]+>', match.group(0))
                tag_id = len(segment_tags); segment_tags.append("".join(all_tags))
                return f"[[t:{tag_id}]]"
            
            final_text = re.sub(r'(?:<[^>]+>)+', tag_replacer_bulk, processed_text)
            
            # 3. INTELLIGENT SPLITTING
            if len(final_text) > 3000:
                sub_parts = split_text_intelligently(final_text)
                for i, part in enumerate(sub_parts):
                    flattened_text[f"{current_path}.sub_{i}"] = {"text": part, "tags": segment_tags}
            else:
                flattened_text[current_path] = {"text": final_text, "tags": segment_tags}

    if target_subtree in data:
        walk(data[target_subtree], f"{path}.{target_subtree}")
    return flattened_text, footnotes

def chunk_dictionary(flattened_dict, max_chars_per_chunk=4000, max_items_per_chunk=3):
    chunks = []
    current_chunk = {}
    current_len = 0
    for k, v in flattened_dict.items():
        text_len = len(v["text"])
        if (current_len + text_len > max_chars_per_chunk or len(current_chunk) >= max_items_per_chunk) and current_chunk:
            chunks.append(current_chunk)
            current_chunk = {}; current_len = 0
        current_chunk[k] = v["text"]
        current_len += text_len
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def translate_worker(chunk):
    user_msg = f"TRANSLATE THESE SEGMENTS:\n{json.dumps(chunk, ensure_ascii=False, indent=2)}"
    total_tokens = int(len(user_msg) / 4) + 500
    rate_limiter.wait_for_limit(total_tokens)
    
    payload = {
        "model": MODEL_TRANS,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + "\n" + GLOSSARY},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    attempts = 0
    while attempts < 5:
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 429:
                # Try to get reset time from headers
                reset_tokens = response.headers.get("x-ratelimit-reset-tokens", "60s")
                reset_requests = response.headers.get("x-ratelimit-reset-requests", "1s")
                
                # Convert '60ms' or '1.2s' to seconds
                def parse_time(t_str):
                    match = re.search(r'([0-9.]+)([a-z]+)', t_str)
                    if not match: return 60
                    val, unit = float(match.group(1)), match.group(2)
                    if unit == 'ms': return val / 1000
                    if unit == 'm': return val * 60
                    return val

                sleep_time = max(parse_time(reset_tokens), parse_time(reset_requests), 75)
                print(f"  [Rate Limit] 429 received. API requested cooldown, sleeping {sleep_time}s...")
                time.sleep(sleep_time + 2) # 2s safety buffer
                continue
                
            response.raise_for_status()
            attempts += 1 # Only increment for non-429 successful-ish attempts
            
            res_data = response.json()
            rate_limiter.add_usage(res_data.get("usage", {}).get("total_tokens", total_tokens))
            raw_text = res_data["choices"][0]["message"]["content"].strip()
            
            # Extract JSON from markdown if needed
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match: raw_text = json_match.group(0)
            
            parsed = json.loads(raw_text)
            for k, v in parsed.items():
                if isinstance(v, str):
                    parsed[k] = re.sub(r'<[^>]+>', '', v) # Stray Tag Sanitizer
            
            if set(parsed.keys()) != set(chunk.keys()):
                print(f"  [Error] Key mismatch. Retrying...")
                continue
            return parsed
            
        except Exception as e:
            print(f"  [Error] Attempt {attempts+1} failed: {e}")
            attempts += 1
            time.sleep(10)
    return None

def run_track(flat_data, track_name):
    print(f"\n=== Starting {track_name} Track (Groq) ===")
    translated_map = {}
    ckpt_file = f"checkpoint_{track_name.lower().replace(' ', '_')}_groq.json"
    if os.path.exists(ckpt_file):
        with open(ckpt_file, 'r') as f:
            translated_map = json.load(f)
        print(f"  [Resuming] Found {len(translated_map)} items already translated.")
    
    remaining = {k: v for k, v in flat_data.items() if k not in translated_map}
    if not remaining:
        print(f"  [Skip] All items already translated.")
        return translated_map

    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    remaining_keys = sorted(remaining.keys(), key=natural_sort_key)
    sorted_remaining = {k: remaining[k] for k in remaining_keys}
    
    chunks = chunk_dictionary(sorted_remaining)
    for i, chunk in enumerate(chunks):
        # Extract context (Part/Chapter) from first key
        first_key = list(chunk.keys())[0]
        context = ""
        parts = first_key.split('.')
        if len(parts) >= 4:
            p_name = parts[2]
            c_name = parts[3]
            if not c_name and len(parts) > 4: c_name = f"Ch.{parts[4]}"
            context = f" ({p_name}, {c_name})"
            
        res = translate_worker(chunk)
        if res:
            translated_map.update(res)
            with open(ckpt_file, 'w') as f:
                json.dump(translated_map, f, indent=2)
            print(f"  [Heartbeat] {track_name}{context}: {i+1}/{len(chunks)} batches complete.")
        else:
            print(f"  [Warning] Batch {i+1} failed.")
    return translated_map

def inject_translation(data_structure, path_string, translated_text, original_entry):
    final_text = translated_text
    if isinstance(original_entry, dict) and "tags" in original_entry:
        for i, tag in enumerate(original_entry["tags"]):
            final_text = final_text.replace(f"[[t:{i}]]", tag)
            
    # Handle sub-segments by joining them if they exist
    # If path ends in .sub_N, we need to find the parent and append
    is_sub = ".sub_" in path_string
    if is_sub:
        parent_path = path_string.rsplit(".sub_", 1)[0]
        keys = parent_path.split('.')[1:]
    else:
        keys = path_string.split('.')[1:]
    
    current = data_structure
    for key in keys[:-1]:
        if key.isdigit(): current = current[int(key)]
        else: current = current[key]
            
    final_key = keys[-1]
    target_idx = int(final_key) if final_key.isdigit() else final_key
    
    if is_sub:
        # Append or Initialize
        if isinstance(current[target_idx], str) and not current[target_idx].startswith("root."):
             current[target_idx] += " " + final_text
        else:
             current[target_idx] = final_text
    else:
        current[target_idx] = final_text
