import re

content = "Littéralement: <i>dût-il être endommagé dans son corps</i>. La version d’Ibn-Tibbon a <span dir=\"rtl\">בעצמו</span>, pour <span dir=\"rtl\">כגופו</span>."

tag_count = 0
def tag_replacer(match):
    global tag_count
    tag_count += 1
    return f"[[t:{tag_count}]]"

# Clean non-i/span tags
content_clean = re.sub(r'<(?!/?(i|span))[^>]+>', '', content)
# Replace tags with [[t:N]]
tag_woven = re.sub(r'<[^>]+>', tag_replacer, content_clean)

print(f"Tag woven: {tag_woven}")
print(f"Total tags: {tag_count}")
