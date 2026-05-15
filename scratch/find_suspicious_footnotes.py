
import json
import re

def find_suspicious_footnotes():
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text_data = data.get("text", {})
    
    suspicious = []
    
    # Footnote regex for nested check
    # We look for <i class="footnote"> ... <i>
    nested_pattern = r'<i class="footnote">.*?<i>'
    
    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{path}.{i}")
        elif isinstance(node, str):
            if '<i class="footnote">' in node:
                # Check for nesting
                # Find all footnotes in this segment
                fns = re.findall(r'<i class="footnote">(.*?)</i>', node, flags=re.DOTALL)
                # If non-greedy findall misses nested content, the leftover text will contain </i>
                # But a better way: check if the footnote content itself has <i>
                
                # Let's use a simpler check: does the segment have <i class="footnote"> AND more than one <i>?
                # Actually, any <i> inside <i class="footnote"> is "suspicious" for our old regex.
                
                matches = re.finditer(r'<i class="footnote">(.*?)</i>', node, flags=re.DOTALL)
                for m in matches:
                    content = m.group(1)
                    if '<i>' in content or '<i ' in content:
                        suspicious.append({
                            "path": path,
                            "snippet": node[:100] + "...",
                            "footnote_content_preview": content[:100] + "..."
                        })

    walk(text_data, "root.text")
    
    print(f"Found {len(suspicious)} segments with potentially nested italics in footnotes.")
    for s in suspicious[:10]: # Show first 10
        print(f"\nPath: {s['path']}")
        print(f"Snippet: {s['snippet']}")
        print(f"FN Preview: {s['footnote_content_preview']}")

if __name__ == "__main__":
    find_suspicious_footnotes()
