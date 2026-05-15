
import json
import re

def count_words(text):
    return len(re.findall(r'\w+', text))

def estimate_tokens(word_count):
    # Llama 3/Groq tokenization is roughly 1.3 - 1.5 tokens per word for mixed French/English/Hebrew
    return int(word_count * 1.4)

def run_estimate():
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Target: Part 1, Chapter 2
    # Based on view_file, it's in data["text"]["Part 1"][""][1]
    chapter_segments = data["text"]["Part 1"][""][1]
    
    total_words_main = 0
    total_words_fns = 0
    fn_count = 0
    
    fn_pattern = r'<sup class="footnote-marker">\(\d+\)</sup><i class="footnote">(.*?)</i>|<i class="footnote">(.*?)</i>'
    
    print(f"--- Part I, Chapter 2 Estimate ---")
    for i, segment in enumerate(chapter_segments):
        # Extract footnotes
        fns = re.findall(fn_pattern, segment, flags=re.DOTALL)
        clean_text = re.sub(fn_pattern, '', segment, flags=re.DOTALL)
        clean_text = re.sub(r'<[^>]+>', '', clean_text) # Strip other HTML tags
        
        seg_words = count_words(clean_text)
        total_words_main += seg_words
        
        seg_fn_words = 0
        for fn in fns:
            fn_text = fn[0] or fn[1]
            fn_text_clean = re.sub(r'<[^>]+>', '', fn_text)
            seg_fn_words += count_words(fn_text_clean)
            fn_count += 1
            
        total_words_fns += seg_fn_words
        print(f"Segment {i+1}: {seg_words} words, {len(fns)} footnotes ({seg_fn_words} words)")

    total_words = total_words_main + total_words_fns
    tokens = estimate_tokens(total_words)
    
    print(f"\nSummary:")
    print(f"Main Text Words: {total_words_main}")
    print(f"Footnote Words: {total_words_fns} ({fn_count} footnotes)")
    print(f"Total Words: {total_words}")
    print(f"Estimated Tokens (Llama 3/Groq): ~{tokens}")
    print(f"TPM Limit: 70,000")
    print(f"Percentage of TPM: {(tokens / 70000) * 100:.1f}%")

if __name__ == "__main__":
    run_estimate()
