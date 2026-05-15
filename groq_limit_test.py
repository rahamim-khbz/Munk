
import json
import os
import re
import time
from groq import Groq

# --- LIMIT TEST CONFIG ---
BATCH_SIZE = 50
MODEL_ID = "llama-3.3-70b-versatile"
OUTPUT_FILE = "groq_limit_test_output.json"

def load_env():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
client = Groq(api_key=os.environ.get("VITE_GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an elite scholarly translator for Salomon Munk. 
Translate the following footnotes. Return JSON ONLY: {"results": [{"id": "...", "text": "..."}]}
Maintain all [[t:N]] tags. Do not truncate. Utilize your full output buffer."""

def main():
    with open("repair_list.json", "r", encoding="utf-8") as f:
        to_repair = json.load(f)

    # Take a giant batch to test limits
    test_batch = to_repair[:BATCH_SIZE]
    model_input = [{"id": b["id"], "text": b["fr_text"]} for b in test_batch]

    print(f"Testing Groq Limit with Batch of {BATCH_SIZE} footnotes...")
    print(f"Est. Input: {len(json.dumps(model_input)) // 4} tokens")

    try:
        start_time = time.time()
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(model_input, ensure_ascii=False)}
            ],
            model=MODEL_ID,
            temperature=0.3,
            max_tokens=32768, # Attempting to max out the buffer
            response_format={"type": "json_object"}
        )
        elapsed = time.time() - start_time
        
        raw_output = chat_completion.choices[0].message.content
        print(f"Response Received in {elapsed:.2f}s")
        print(f"Response Length: {len(raw_output):,} characters")
        
        # Try to parse to verify integrity
        data = json.loads(raw_output)
        print(f"SUCCESS: Successfully parsed {len(data['results'])} footnotes.")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"LIMIT REACHED OR ERROR: {e}")
        # Print the last 100 chars to see where it cut off
        if 'raw_output' in locals():
            print(f"End of response: ...{raw_output[-100:]}")

if __name__ == "__main__":
    main()
