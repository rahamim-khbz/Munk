import sys
import re

filename = "Munk Viewer.html"

with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = r"""function showFn(id) {
            const raw = footnotes[id];
            const num = id.replace('fn.', '');
            const text = raw ? raw.replace(/\[\[t:\d+\]\]/g, '').replace(/\[\[fn:\d+\]\]/g, '') : null;
            
            const panel = document.getElementById('fn-panel');
            const currentLabel = document.getElementById('fn-panel-label').textContent;
            
            if (panel.classList.contains('open') && currentLabel === `Note ${num}`) {
                closeFnPanel();
                return;
            }
            
            document.getElementById('fn-panel-label').textContent = `Note ${num}`;
            document.getElementById('fn-panel-body').innerHTML = text 
                ? text 
                : '<em>Footnote translation still in progress...</em>';
                
            panel.classList.add('open');
            document.querySelector('.main-container').classList.add('fn-open');
        }"""

pattern = re.compile(r"function showFn\(id\) \{.*?\n        \}", re.DOTALL)
match = pattern.search(content)

if match:
    new_content = content[:match.start()] + replacement + content[match.end():]
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated Munk Viewer.html")
else:
    print("Function not found!")
