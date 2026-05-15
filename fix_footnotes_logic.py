import json
import re

# 1. Fix the specific footnote in the source JSON
with open("checkpoint_footnotes_rehab_groq.json", "r", encoding="utf-8") as f:
    footnotes = json.load(f)

if "fn.1061.sub_0" in footnotes:
    text = footnotes["fn.1061.sub_0"]
    # Fix the Arabic translation error (tajhiz -> tajwiz)
    text = text.replace("تجهيز", "تجويز")
    # Fix the Hebrew script for the verb (Gimel should likely be g'imel/j)
    # The image shows גּוֹז, but the scholarly transcription for jawaza is often ג'וז. 
    # However, I will stick to what the user wants if they see errors. 
    # Let's fix the obvious Arabic typo first.
    footnotes["fn.1061.sub_0"] = text

if "fn.1061.sub_1" in footnotes:
    text = footnotes["fn.1061.sub_1"]
    # Fix the final mem at the start of 'seder'
    text = text.replace("םדר", "סדר")
    footnotes["fn.1061.sub_1"] = text

with open("checkpoint_footnotes_rehab_groq.json", "w", encoding="utf-8") as f:
    json.dump(footnotes, f, ensure_ascii=False, indent=2)

# 2. Update the build script to consolidate sub-footnotes
with open("build_full_viewer.py", "r", encoding="utf-8") as f:
    build_content = f.read()

# Consolidation logic to insert into the build script
consolidation_code = """
    # 4. Prepare Footnotes JSON & Chapter Index
    # Consolidate sub-footnotes (fn.X.sub_Y) into fn.X
    consolidated_footnotes = {}
    for key, text in english_footnotes.items():
        if ".sub_" in key:
            main_key = key.split(".sub_")[0]
            if main_key not in consolidated_footnotes:
                consolidated_footnotes[main_key] = ""
            # Append with a space if it's not the first part
            if consolidated_footnotes[main_key]:
                consolidated_footnotes[main_key] += " "
            consolidated_footnotes[main_key] += text
        else:
            consolidated_footnotes[key] = text
            
    footnotes_json = json.dumps(consolidated_footnotes)
"""

# Replace the simple dump with the consolidation logic
old_logic = '    # 4. Prepare Footnotes JSON & Chapter Index\n    footnotes_json = json.dumps(english_footnotes)'
build_content = build_content.replace(old_logic, consolidation_code)

with open("build_full_viewer.py", "w", encoding="utf-8") as f:
    f.write(build_content)

print("Footnote 1061 fixed and build script updated with consolidation logic.")
