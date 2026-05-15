
import os

file_path = "/Users/rayhabbaz/Munk's Guide/Munk Viewer.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the en-cell style
old_style = '.en-cell { font-size: 1.1rem; line-height: 1.7; text-align: justify; }'
new_style = '.en-cell { \n            font-family: var(--english-font), var(--hebrew-font);\n            font-size: 1.1rem; \n            line-height: 1.7; \n            text-align: justify; \n        }'

if old_style in content:
    content = content.replace(old_style, new_style)
    print("Replaced .en-cell style.")
else:
    print("Could not find .en-cell style exactly. Trying regex.")
    import re
    content, count = re.subn(r'\.en-cell\s*\{[^}]*\}', new_style, content)
    if count > 0:
        print(f"Replaced .en-cell style using regex ({count} occurrences).")
    else:
        print("Regex failed too.")

# Also add it to fn-panel-body for footnotes
old_fn_style = '.fn-panel-body {'
new_fn_style = '.fn-panel-body {\n            font-family: var(--english-font), var(--hebrew-font);'

if old_fn_style in content and 'var(--hebrew-font)' not in content.split('.fn-panel-body')[1].split('}')[0]:
    content = content.replace(old_fn_style, new_fn_style)
    print("Updated .fn-panel-body style.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
