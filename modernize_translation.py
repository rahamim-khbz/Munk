#!/usr/bin/env python3
"""
modernize_translation.py — Systematically modernizes archaic English second-person
pronouns and verb inflections across the master translated dataset nested under the "text" key.
"""

import json
import re
import os
import shutil
from datetime import datetime

def backup_file(filepath):
    if os.path.exists(filepath):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{filepath}.bak_{ts}"
        shutil.copy2(filepath, backup)
        print(f"  [Backup] Created {os.path.basename(backup)}")
        return backup
    return None

def modernize_text(text):
    orig_text = text
    
    # 1. Explicit multi-word verb phrases
    phrases = [
        (r"\bThou art\b", "You are"), (r"\bthou art\b", "you are"),
        (r"\bThou didst\b", "You did"), (r"\bthou didst\b", "you did"),
        (r"\bThou dost\b", "You do"), (r"\bthou dost\b", "you do"),
        (r"\bThou hast\b", "You have"), (r"\bthou hast\b", "you have"),
        (r"\bThou shalt\b", "You will"), (r"\bthou shalt\b", "you will"),
        (r"\bThou wilt\b", "You will"), (r"\bthou wilt\b", "you will"),
        (r"\bThou wert\b", "You were"), (r"\bthou wert\b", "you were"),
        (r"\bThou mayest\b", "You may"), (r"\bthou mayest\b", "you may"),
        (r"\bThou canst\b", "You can"), (r"\bthou canst\b", "you can"),
        (r"\bThou shouldst\b", "You should"), (r"\bthou shouldst\b", "you should"),
        (r"\bThou wouldst\b", "You would"), (r"\bthou wouldst\b", "you would"),
        
        # Additional specific verb forms mapped directly
        (r"\bThou knowest\b", "You know"), (r"\bthou knowest\b", "you know"),
        (r"\bThou seest\b", "You see"), (r"\bthou seest\b", "you see"),
        (r"\bThou findest\b", "You find"), (r"\bthou findest\b", "you find"),
        (r"\bThou understandest\b", "You understand"), (r"\bthou understandest\b", "you understand"),
        (r"\bThou divestest\b", "You divest"), (r"\bthou divestest\b", "you divest"),
        (r"\bThou haltest\b", "You halt"), (r"\bthou haltest\b", "you halt"),
        (r"\bThou deceivest\b", "You deceive"), (r"\bthou deceivest\b", "you deceive"),
        (r"\bThou aspirest\b", "You aspire"), (r"\bthou aspirest\b", "you aspire"),
        (r"\bThou joinest\b", "You join"), (r"\bthou joinest\b", "you join"),
        (r"\bThou renderest\b", "You render"), (r"\bthou renderest\b", "you render"),
        (r"\bThou provokest\b", "You provoke"), (r"\bthou provokest\b", "you provoke"),
        (r"\bThou enkindlest\b", "You enkindle"), (r"\bthou enkindlest\b", "you enkindle"),
        (r"\bThou devotest\b", "You devote"), (r"\bthou devotest\b", "you devote"),
        (r"\bThou ponderest\b", "You ponder"), (r"\bthou ponderest\b", "you ponder"),
        (r"\bThou believest\b", "You believe"), (r"\bthou believest\b", "you believe"),
        (r"\bThou acceptest\b", "You accept"), (r"\bthou acceptest\b", "you accept"),
        (r"\bThou desirest\b", "You desire"), (r"\bthou desirest\b", "you desire"),
        (r"\bThou pleasest\b", "You please"), (r"\bthou pleasest\b", "you please"),
        (r"\bThou occupiest\b", "You occupy"), (r"\bthou occupiest\b", "you occupy"),
        (r"\bThou walkest\b", "You walk"), (r"\bthou walkest\b", "you walk"),
        (r"\bThou prayest\b", "You pray"), (r"\bthou prayest\b", "you pray"),
        (r"\bThou readest\b", "You read"), (r"\bthou readest\b", "you read"),
        (r"\bThou performest\b", "You perform"), (r"\bthou performest\b", "you perform"),
        (r"\bThou contentest\b", "You content"), (r"\bthou contentest\b", "you content"),
        (r"\bThou conversest\b", "You converse"), (r"\bthou conversest\b", "you converse"),
        (r"\bThou speakest\b", "You speak"), (r"\bthou speakest\b", "you speak"),
        (r"\bThou sinnest\b", "You sin"), (r"\bthou sinnest\b", "you sin"),
        (r"\bThou fulfillest\b", "You fulfill"), (r"\bthou fulfillest\b", "you fulfill"),
        
        # Common prepositions/phrases with thee
        (r"\bbehoovs thee\b", "behooves you"), (r"\bbehooves thee\b", "behooves you"),
        (r"\bunto thee\b", "to you"), (r"\bUnto thee\b", "To you"),
        (r"\bto thee\b", "to you"), (r"\bTo thee\b", "To you"),
        (r"\bfrom thee\b", "from you"), (r"\bFrom thee\b", "From you"),
        (r"\bfor thee\b", "for you"), (r"\bFor thee\b", "For you"),
        (r"\bwith thee\b", "with you"), (r"\bWith thee\b", "With you"),
        (r"\bby thee\b", "by you"), (r"\bBy thee\b", "By you"),
        (r"\bin thee\b", "in you"), (r"\bIn thee\b", "In you"),
        (r"\bof thee\b", "of you"), (r"\bOf thee\b", "Of you"),
        (r"\bon thee\b", "on you"), (r"\bOn thee\b", "On you"),
        (r"\bupon thee\b", "upon you"), (r"\bUpon thee\b", "Upon you"),
        (r"\bbefalls thee\b", "befalls you"), (r"\bimpells thee\b", "impels you"),
    ]
    
    for pattern, repl in phrases:
        text = re.sub(pattern, repl, text)
        
    # 2. General dynamic catch-all for remaining "thou <verbest>" patterns
    def fix_est_verb(match):
        pronoun = match.group(1)
        verb = match.group(2)
        base_verb = verb
        if verb.endswith("i"): base_verb = verb[:-1] + "y"
        elif verb == "do": base_verb = "do"
        new_pronoun = "You" if pronoun.istitle() else "you"
        return f"{new_pronoun} {base_verb}"

    text = re.sub(r"\b(Thou|thou)\s+([a-zA-Z]+?)(?:est|st)\b", fix_est_verb, text)
    
    # 3. Standalone archaic pronouns mapping
    text = re.sub(r"\bThou\b", "You", text)
    text = re.sub(r"\bthou\b", "you", text)
    text = re.sub(r"\bThee\b", "You", text)
    text = re.sub(r"\bthee\b", "you", text)
    text = re.sub(r"\bThy\b", "Your", text)
    text = re.sub(r"\bthy\b", "your", text)
    text = re.sub(r"\bThine\b", "Your", text)
    text = re.sub(r"\bthine\b", "your", text)
    
    return text, text != orig_text

def main():
    print("=" * 70)
    print("  SYSTEMATIC ARCHAIC TRANSLATION MODERNIZER (NESTED)")
    print("=" * 70)
    
    target_json = "munk_production_v1.json"
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        return
        
    backup_file(target_json)
    
    with open(target_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    updates = 0
    # Process main segments in data["text"]
    if "text" in data and isinstance(data["text"], dict):
        for key, val in data["text"].items():
            if isinstance(val, str):
                new_val, changed = modernize_text(val)
                if changed:
                    data["text"][key] = new_val
                    updates += 1
                    
    if updates > 0:
        with open(target_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Successfully modernized {updates} segments in {target_json}.")
    else:
        print("  ℹ️ No archaic terms found to update.")
        
if __name__ == "__main__":
    main()
