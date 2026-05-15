import json
import random
import re

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten_text(t):
    if isinstance(t, list): return ' '.join(flatten_text(x) for x in t)
    return t or ''

def build_segment_list(data, text_key='french'):
    segments = []
    
    # 1. Letter to R Joseph
    letter = data['text'].get('Letter to R Joseph son of Judah', [])
    for i, t in enumerate(letter):
        txt = flatten_text(t).strip()
        if txt:
            segments.append({
                'ref': f'Guide_for_the_Perplexed_Letter_to_R_Joseph_son_of_Judah.{i+1}',
                'chapter': 'Letter',
                'paragraph': i + 1,
                text_key: txt
            })

    # 2. Prefatory Remarks
    prefatory = data['text'].get('Prefatory Remarks', [])
    for i, t in enumerate(prefatory):
        txt = flatten_text(t).strip()
        if txt:
            segments.append({
                'ref': f'Guide_for_the_Perplexed_Prefatory_Remarks.{i+1}',
                'chapter': 'Prefatory',
                'paragraph': i + 1,
                text_key: txt
            })

    # 3. Parts 1, 2, 3
    for part in ['Part 1', 'Part 2', 'Part 3']:
        part_data = data['text'].get(part, {})
        if not part_data: continue

        # Introduction for the Part
        for i, t in enumerate(part_data.get('Introduction', [])):
            txt = flatten_text(t).strip()
            if txt:
                segments.append({
                    'ref': f'Guide_for_the_Perplexed_{part.replace(" ", "_")}_Introduction.{i+1}',
                    'chapter': f'{part} Intro',
                    'paragraph': i + 1,
                    text_key: txt
                })

        # Chapters for the Part
        chapters = part_data.get('', [])
        for ch_idx, chapter_paras in enumerate(chapters):
            ch = ch_idx + 1
            for i, t in enumerate(chapter_paras):
                txt = flatten_text(t).strip()
                if txt:
                    segments.append({
                        'ref': f'Guide_for_the_Perplexed_{part.replace(" ", "_")}.{ch}.{i+1}',
                        'chapter': f'{part} Ch {ch}',
                        'paragraph': i + 1,
                        text_key: txt
                    })
    return segments

def get_first_ten_words(segments, reverse_words=False):
    """Joins chapter segments, strips HTML, and extracts the first ten words."""
    if not segments:
        return "[Empty Chapter]"
    
    # Join all segments into a single string
    full_text = " ".join(segments)
    # Strip HTML tags
    clean_text = re.sub(r'<[^>]+>', '', full_text)
    # Normalize whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    words = clean_text.split()
    sample = words[:10]
    if reverse_words:
        sample = sample[::-1]
        
    return " ".join(sample)

def verify_translations(french_file, munk_file, maqbili_file):
    # 1. Load the JSON files
    try:
        french_data_raw = load_json(french_file)
        munk_data_raw = load_json(munk_file)
        maqbili_data_raw = load_json(maqbili_file)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    # Process French segments
    french_segments = build_segment_list(french_data_raw, 'french')
    french_data = {}
    for s in french_segments:
        french_data.setdefault(s['chapter'], []).append(s['french'])
        
    # Process Munk translation segments
    munk_data = {}
    if 'segments' in munk_data_raw:
        for ref, s in munk_data_raw['segments'].items():
            munk_data.setdefault(s['chapter'], []).append(s.get('english', ''))
    else:
        for s in munk_data_raw.values():
            munk_data.setdefault(s.get('chapter', 'Unknown'), []).append(s.get('english', ''))

    # Process Maqbili segments (using full JSON structure from Downloads)
    maqbili_segments = build_segment_list(maqbili_data_raw, 'hebrew')
    maqbili_data = {}
    for s in maqbili_segments:
        maqbili_data.setdefault(s['chapter'], []).append(s['hebrew'])

    french_chapters = list(french_data.keys())
    munk_chapters = list(munk_data.keys())
    maqbili_chapters = list(maqbili_data.keys())

    print("### Chapter Order Check ###")
    # 2. Check chapter order and count
    if french_chapters == munk_chapters == maqbili_chapters:
        print("✅ Chapter order and naming match perfectly across all 3 files.\n")
    else:
        print("❌ Chapter order or naming DOES NOT match.")
        print(f"   French total chapters: {len(french_chapters)}")
        print(f"   Munk total chapters: {len(munk_chapters)}")
        print(f"   Maqbili total chapters: {len(maqbili_chapters)}\n")

    print("### Segment Count Check ###")
    # 3. Check segment counts per chapter
    mismatches = []
    for chapter in french_chapters:
        f_len = len(french_data.get(chapter, []))
        m_len = len(munk_data.get(chapter, [])) if chapter in munk_data else 0
        maq_len = len(maqbili_data.get(chapter, [])) if chapter in maqbili_data else 0
        
        # Only report mismatch if there's a difference between French and the others (ignoring empty/missing Munk/Maqbili if they are still building)
        if (chapter in munk_data and f_len != m_len) or (chapter in maqbili_data and f_len != maq_len):
            mismatches.append((chapter, f_len, m_len, maq_len))
    
    if not mismatches:
        print("✅ Segment counts match for all available chapters.\n")
    else:
        print("❌ Segment count mismatches found:")
        for ch, f_len, m_len, maq_len in mismatches:
            print(f"   - {ch}: French: {f_len} | Munk: {m_len} | Maqbili: {maq_len}")
        print("\n")

    print("### Visual Confirmation: First 10 Words of 10 Random Chapters ###")
    # 4. Select 10 random chapters (or fewer if the text has less than 10 chapters)
    sample_size = min(10, len(french_chapters))
    sampled_chapters = random.sample(french_chapters, sample_size)

    for chapter in sampled_chapters:
        print(f"\nChapter: {chapter}")
        
        # French output
        french_words = get_first_ten_words(french_data[chapter])
        print(f"  French : {french_words}")
        
        # Munk output
        if chapter in munk_data:
            munk_words = get_first_ten_words(munk_data[chapter])
            print(f"  Munk   : {munk_words}")
        else:
            print("  Munk   : [Chapter Missing]")

        # Maqbili output
        if chapter in maqbili_data:
            # We reverse the words for Maqbili to simulate 'Visual RTL' in LTR terminals.
            # This puts the first word on the right.
            maqbili_words = get_first_ten_words(maqbili_data[chapter], reverse_words=True)
            print(f"  Maqbili: {maqbili_words}")
        else:
            print("  Maqbili: [Chapter Missing]")

if __name__ == "__main__":
    FRENCH_FILE = "French.json"
    MUNK_FILE = "/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide/munk_translations.json"
    MAQBILI_FILE = "/Users/rayhabbaz/Downloads/Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json"
    
    verify_translations(FRENCH_FILE, MUNK_FILE, MAQBILI_FILE)
