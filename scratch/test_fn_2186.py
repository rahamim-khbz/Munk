import os
import json
import re
from munk_pipeline_groq import extract_and_flatten
from munk_pipeline_groq_rehab_v3 import translate_worker_groq_rehab

# Mock the flat_footnotes for fn.2186
fn_id = "fn.2186"
fn_content = "Littéralement: <i>dût-il être endommagé dans son corps</i>. La version d’Ibn-Tibbon a <span dir=\"rtl\">בעצמו</span>, pour <span dir=\"rtl\">כגופו</span>."

# Tag weaving simulation
tag_count = 0
def tag_replacer(match):
    global tag_count
    tag_count += 1
    return f"[[t:{tag_count}]]"

# Clean non-i/span tags
content_clean = re.sub(r'<(?!/?(i|span))[^>]+>', '', fn_content)
tag_woven = re.sub(r'<[^>]+>', tag_replacer, content_clean)

fn_data = {'text': tag_woven}

print(f"Testing {fn_id} with tag-woven text: {tag_woven}")

# We need the API key
from dotenv import load_dotenv
load_dotenv()

result = translate_worker_groq_rehab(fn_id, fn_data)
if result:
    print(f"SUCCESS: {result}")
else:
    print("FAILED")
