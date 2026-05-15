
import json
import re

# Words ending in 'eth' that are legitimate and should NOT be changed
EXCLUDE_LIST = {
    'beth', 'daleth', 'seth', 'teeth', 'beneath', 'shibboleth', 'death', 'breath', 
    'nazareth', 'elizabeth', 'breadth', 'hundredth', 'thousandth', 'twentieth',
    'thirtyeth', 'fortieth', 'fiftieth', 'sixtieth', 'seventieth', 'eightieth', 'ninetieth',
    'maccabieth', 'kohéleth', 'koheleth', 'ameth'
}

# Explicit mapping for non-eth archaisms or tricky ones
EXPLICIT_MAP = {
    r'\bhath\b': 'has',
    r'\bdoth\b': 'does',
    r'\bsaith\b': 'says',
    r'\bwhereof\b': 'of which',
    r'\bhereof\b': 'of this',
    r'\bwherein\b': 'in which',
    r'\bbetwixt\b': 'between',
    r'\bwhensoever\b': 'whenever',
    r'\bforsooth\b': 'indeed',
    r'\bhowbeit\b': 'however',
    r'\bperadventure\b': 'perhaps',
}

ETH_PATTERN = re.compile(r'\b(\w+)(eth)\b', re.IGNORECASE)

def fix_eth_match(match):
    word = match.group(0)
    stem = match.group(1)
    suffix = match.group(2) # eth or ETH or Eth
    
    if word.lower() in EXCLUDE_LIST:
        return word
        
    # Handle capitalization
    is_title = word.istitle()
    is_upper = word.isupper()
    
    stem_lower = stem.lower()
    
    # Verb ending rules:
    if stem_lower.endswith(('sh', 'ch', 'ss', 'x', 'z', 'o')):
        new_suffix = "es"
    elif stem_lower.endswith('i') and not stem_lower.endswith(('ai', 'ei', 'oi', 'ui')):
        # Usually ieth (e.g. flieth -> flies)
        # But we need to be careful. 
        # If it ends in 'i', it might be 'y' originally.
        new_suffix = "es" # stem + es? (e.g. fly -> flies)
    else:
        new_suffix = "s"
        
    if is_title:
        return stem.capitalize() + new_suffix
    if is_upper:
        return stem.upper() + new_suffix.upper()
    return stem + new_suffix

def fix_text(text):
    if not isinstance(text, str):
        return text
    
    # 1. Apply explicit mapping
    for pattern, replacement in EXPLICIT_MAP.items():
        reg = re.compile(pattern, re.IGNORECASE)
        def repl_explicit(match):
            orig = match.group(0)
            if orig.istitle(): return replacement.capitalize()
            if orig.isupper(): return replacement.upper()
            return replacement
        text = reg.sub(repl_explicit, text)
        
    # 2. Apply generalized -eth fix
    text = ETH_PATTERN.sub(fix_eth_match, text)
    
    return text

FILES_TO_FIX = [
    "checkpoint_footnotes_rehab_groq.json",
    "checkpoint_main_text_groq.json"
]

def main():
    for filename in FILES_TO_FIX:
        try:
            print(f"Processing {filename}...")
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            changes_made = 0
            fixed_data = {}
            
            for k, v in data.items():
                fixed_v = fix_text(v)
                if fixed_v != v:
                    changes_made += 1
                fixed_data[k] = fixed_v
                
            if changes_made > 0:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                print(f"  ✅ Fixed archaic forms in {changes_made} entries.")
            else:
                print(f"  ✓ No archaic forms found.")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    main()
