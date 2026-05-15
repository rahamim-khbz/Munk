
import json
import os
import re

def count_words(text):
    return len(re.findall(r'\w+', text))

def estimate_tokens(word_count):
    return int(word_count * 1.5)

def run_remaining_estimate():
    source_path = 'French_Arabic_Enriched.json'
    ckpt_path = 'checkpoint_footnotes_gemini.json'
    
    if not os.path.exists(source_path):
        print(f"Source file {source_path} not found.")
        return

    # Load Source
    with open(source_path, 'r') as f:
        data = json.load(f)
    
    # Simple extraction of footnotes to count
    all_footnotes = []
    
    def walk(node):
        if isinstance(node, dict):
            for v in node.values(): walk(v)
        elif isinstance(node, list):
            for v in node: walk(v)
        elif isinstance(node, str):
            # Regex for footnotes
            fns = re.findall(r'<i class="footnote">(.*?)</i>', node, flags=re.DOTALL)
            for fn in fns:
                # Strip tags
                clean = re.sub(r'<[^>]+>', '', fn)
                all_footnotes.append(clean)

    walk(data['text'])
    total_fns_in_source = len(all_footnotes)
    
    # Load Checkpoint
    translated_count = 0
    if os.path.exists(ckpt_path):
        with open(ckpt_path, 'r') as f:
            translated_map = json.load(f)
            translated_count = len(translated_map)
            
    # We estimate the remaining words by looking at the last few footnotes if we don't have the exact IDs
    # But we can just count the untranslated ones.
    # Actually, the 3207 vs 4030 count from the MD report is more reliable.
    
    total_total = 4030
    remaining_count = total_total - translated_count
    
    # Calculate average word count from the footnotes we found
    avg_words = sum(count_words(f) for f in all_footnotes) / len(all_footnotes) if all_footnotes else 0
    
    estimated_remaining_words = remaining_count * avg_words
    tokens = estimate_tokens(estimated_remaining_words)
    
    print(f"--- Remaining Footnote Estimate (Self-Contained) ---")
    print(f"Total Footnotes in Source: {total_total}")
    print(f"Translated: {translated_count}")
    print(f"Remaining: {remaining_count}")
    print(f"Average Words per Footnote: {avg_words:.1f}")
    print(f"Estimated Remaining Words: {int(estimated_remaining_words)}")
    print(f"Estimated Tokens: ~{tokens}")
    
    # Groq Speed
    tpm_limit = 70000 # Standard Llama 3 70B limit
    minutes = tokens / tpm_limit
    
    print(f"\nCompletion Estimate (Groq):")
    print(f"- Pure Processing Time: {minutes:.1f} minutes")
    print(f"- With 3 RPM limit (current script): ~{(remaining_count / 5) / 3:.1f} hours (assuming 5 fns per batch)")
    print(f"- With 30 RPM limit: ~{(remaining_count / 5) / 30:.1f} minutes")

if __name__ == "__main__":
    run_remaining_estimate()
