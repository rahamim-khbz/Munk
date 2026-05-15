import json
import sys
import os

def validate_json_iterative(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # Check if it's likely a JSONL file
    is_jsonl = filepath.endswith('.jsonl')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        f.seek(0)
        
        # Heuristic for JSONL: if the first line is valid JSON and there's more than one line
        if not is_jsonl:
            try:
                json.loads(first_line)
                # If we're here, the first line is valid. Check if there are more lines.
                lines = f.readlines()
                if len(lines) > 1:
                    is_jsonl = True
                f.seek(0)
            except:
                f.seek(0)

    max_errors = 50
    if is_jsonl:
        print(f"Scanning {filepath} as JSONL (line-by-line)...")
        with open(filepath, 'r', encoding='utf-8') as f:
            error_count = 0
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    error_count += 1
                    print(f"\n❌ [Line {i}] JSONL Error: {e.msg}")
                    print(f"   Snippet: {line[:100]}...")
                    if error_count >= 50:
                        print("Too many errors, stopping.")
                        break
            if error_count == 0:
                print("✅ JSONL is valid!")
    else:
        print(f"Scanning {filepath} as a single JSON object...")
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()

        current_content = list(original_content)
        error_count = 0
        
        while error_count < max_errors:
            content_str = "".join(current_content)
            try:
                json.loads(content_str)
                if error_count == 0:
                    print("✅ JSON is valid!")
                else:
                    print(f"\n✅ No more errors found after {error_count} bypasses.")
                break
            except json.JSONDecodeError as e:
                error_count += 1
                print(f"\n❌ Error #{error_count} found at line {e.lineno}, column {e.colno}:")
                print(f"   Message: {e.msg}")
                
                # Show context
                lines = content_str.splitlines()
                if 0 < e.lineno <= len(lines):
                    print(f"   Context: {lines[e.lineno-1].strip()}")
                
                # Bypass the error by replacing the character at e.pos with a space
                if e.pos < len(current_content):
                    current_content[e.pos] = ' '
                else:
                    break
    
    if error_count >= max_errors:
        print(f"\nReached limit of {max_errors} errors. There may be more.")

if __name__ == "__main__":
    # Default to the enriched file if no argument provided
    target_file = 'French_Arabic_Enriched.json'
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    validate_json_iterative(target_file)
