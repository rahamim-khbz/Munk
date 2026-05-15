
import json
import re

def count_words(text):
    return len(re.findall(r'\w+', text))

def estimate_tokens(word_count):
    return int(word_count * 1.4)

def run_total_estimate():
    # 1. Static Overheads
    system_prompt = '''Translate French to English. Adopt a serious Victorian scholarly prose style.
- Preserve Hebrew/Arabic script.
- Translate Latin inline in [Lat.: ...].
- Preserve markers [[fn:N]] and [[t:N]] exactly.
Return ONLY a JSON object with the original keys.
'''
    glossary = ''' TERMINOLOGY GLOSSARY
  intellect          -> intellect
  entendement        -> understanding
  forme              -> form
  matière            -> matter
  faculté            -> faculty
'''
    overhead_text = system_prompt + glossary + "TRANSLATE THESE SEGMENTS:\n"
    overhead_words = count_words(overhead_text)
    overhead_tokens = estimate_tokens(overhead_words)
    
    # 2. Chapter 2 Content
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapter_segments = data["text"]["Part 1"][""][1]
    
    # We'll simulate the chunking: 3000 chars per chunk
    chunks = []
    current_chunk = []
    current_len = 0
    for seg in chapter_segments:
        if current_len + len(seg) > 3000 and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_len = 0
        current_chunk.append(seg)
        current_len += len(seg)
    if current_chunk:
        chunks.append(current_chunk)
        
    print(f"--- Full Token Estimate (Chapter 2 Pilot) ---")
    print(f"Number of Chunks: {len(chunks)}")
    print(f"Overhead per chunk (System + Glossary + JSON overhead): ~{overhead_tokens + 50} tokens")
    
    total_tokens_all_chunks = 0
    for i, chunk in enumerate(chunks):
        chunk_text = json.dumps(chunk, ensure_ascii=False)
        chunk_words = count_words(chunk_text)
        chunk_tokens = estimate_tokens(chunk_words) + overhead_tokens
        
        total_tokens_all_chunks += chunk_tokens
        print(f"Chunk {i+1}: ~{chunk_tokens} tokens ({len(chunk)} segments)")
        
    print(f"\nTOTAL ESTIMATED TOKENS FOR PILOT: ~{total_tokens_all_chunks}")
    print(f"Average tokens per request: ~{total_tokens_all_chunks / len(chunks):.0f}")

if __name__ == "__main__":
    run_total_estimate()
