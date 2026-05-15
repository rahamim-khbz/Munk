import json

def flatten_text(t):
    if isinstance(t, list): return ' '.join(flatten_text(x) for x in t)
    return t or ''

def build_segment_list(data):
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
                    })
    return segments

def generate_report():
    with open('French.json', 'r', encoding='utf-8') as f:
        french_data = json.load(f)
        
    munk_path = '/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide/munk_translations.json'
    with open(munk_path, 'r', encoding='utf-8') as f:
        munk_data = json.load(f)
        
    translated_refs = set(munk_data.get('segments', {}).keys())
    
    expected_segments = build_segment_list(french_data)
    
    # Group by chapter
    chapters = {}
    for s in expected_segments:
        ch = s['chapter']
        if ch not in chapters:
            chapters[ch] = {'total': 0, 'translated': 0, 'missing_refs': [], 'segments': []}
        
        chapters[ch]['total'] += 1
        
        status = 'Missing'
        if s['ref'] in translated_refs:
            chapters[ch]['translated'] += 1
            status = 'Translated'
        else:
            chapters[ch]['missing_refs'].append(s['ref'])
            
        chapters[ch]['segments'].append({
            'ref': s['ref'],
            'status': status
        })
            
    # Write Markdown
    with open('translation_status_report.md', 'w') as f:
        f.write("# Translation Status Report\n\n")
        
        total_segs = len(expected_segments)
        total_trans = len(translated_refs)
        f.write(f"**Total Segments (Source):** {total_segs}  \n")
        f.write(f"**Total Translated:** {total_trans}  \n")
        f.write(f"**Progress:** {(total_trans/total_segs)*100:.1f}%  \n\n")
        
        f.write("## Chapter Summary\n\n")
        f.write("| Chapter | Total Segments | Translated | Status |\n")
        f.write("|---|---|---|---|\n")
        
        for ch, stats in chapters.items():
            total = stats['total']
            trans = stats['translated']
            status = "✅ Complete" if trans == total else f"❌ Missing {total - trans}"
            if trans == 0:
                status = "⏳ Pending"
            f.write(f"| {ch} | {total} | {trans} | {status} |\n")
            
        f.write("\n## Detailed Segment Status\n\n")
        f.write("Only showing chapters with incomplete translations.\n\n")
        
        for ch, stats in chapters.items():
            total = stats['total']
            trans = stats['translated']
            
            if trans > 0 and trans < total:
                f.write(f"### {ch}\n")
                f.write("| Segment Ref | Status |\n")
                f.write("|---|---|\n")
                for s in stats['segments']:
                    icon = "✅" if s['status'] == 'Translated' else "❌"
                    f.write(f"| `{s['ref']}` | {icon} {s['status']} |\n")
                f.write("\n")

if __name__ == '__main__':
    generate_report()
