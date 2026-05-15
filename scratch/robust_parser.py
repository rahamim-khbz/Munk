
import re

def find_balanced_tag(text, start_index, open_tag_pattern, close_tag):
    """
    Finds the content of a balanced tag starting at start_index.
    Supports nesting.
    """
    # Find the end of the opening tag
    match = re.search(open_tag_pattern, text[start_index:])
    if not match:
        return None, None
    
    tag_start = start_index + match.start()
    content_start = start_index + match.end()
    
    stack = 1
    # Use a simple scanner for closing tags and potential nested opening tags
    # This is a bit simplistic but works for <i> tags
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

def extract_and_flatten_robust(data, path="root", target_subtree="text"):
    """
    Stack-based parser to handle nested footnotes and tags correctly.
    """
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
            # 1. Extract Footnotes using Balanced Parser
            text = node
            pos = 0
            processed_text = ""
            
            # Find all <sup class="footnote-marker"> markers
            marker_pattern = r'<sup class="footnote-marker">\(\d+\)</sup>\s*<i class="footnote">|<i class="footnote">'
            
            while True:
                match = re.search(marker_pattern, text[pos:])
                if not match:
                    processed_text += text[pos:]
                    break
                
                # Append text before the match
                processed_text += text[pos:pos+match.start()]
                
                # Use balanced parser to find the end of the <i class="footnote">
                content, end_pos = find_balanced_tag(text, pos + match.start(), r'<i class="footnote">', '</i>')
                
                if content is not None:
                    # Clean the footnote content (tags)
                    fn_tags = []
                    def fn_tag_sub(m):
                        t = m.group(0)
                        tid = len(fn_tags)
                        fn_tags.append(t)
                        return f"[[t:{tid}]]"
                    
                    fn_text_clean = re.sub(r'<[^>]+>', fn_tag_sub, content)
                    
                    fn_id = f"fn.{fn_counter[0]}"
                    footnotes[fn_id] = {"text": fn_text_clean, "tags": fn_tags}
                    processed_text += f"[[fn:{fn_counter[0]}]]"
                    fn_counter[0] += 1
                    pos = end_pos
                else:
                    # Fallback if balanced parsing fails
                    processed_text += text[pos + match.start() : pos + match.end()]
                    pos += match.end()

            # 2. Extract tags from the remaining main text with Tag Merging
            segment_tags = []
            def tag_replacer_bulk(match):
                all_tags = re.findall(r'<[^>]+>', match.group(0))
                tag_content = "".join(all_tags)
                tag_id = len(segment_tags)
                segment_tags.append(tag_content)
                return f"[[t:{tag_id}]]"
            
            tag_pattern_bulk = r'(?:<[^>]+>)+'
            final_text = re.sub(tag_pattern_bulk, tag_replacer_bulk, processed_text)
            
            flattened_text[current_path] = {"text": final_text, "tags": segment_tags}

    if target_subtree in data:
        walk(data[target_subtree], f"{path}.{target_subtree}")
    
    return flattened_text, footnotes
