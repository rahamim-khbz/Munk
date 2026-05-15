
import json
import os
import re
from groq import Groq

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
Translate the French footnote into high-fidelity English.
Preserve all [[t:N]] and [[fn:N]] tags exactly. Maintain dense academic tone.
Output the translated text ONLY."""

def translate(text, model):
    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        model=model,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()

def wc(text):
    return len(re.findall(r'\w+', text))

# Pick 5 representative footnotes from the repair list
# Mix of short, medium, and one long
with open("repair_list.json", "r", encoding="utf-8") as f:
    repairs = json.load(f)

# Pick first short, medium, and long ones
samples = []
for r in repairs:
    w = wc(r["fr_text"])
    if w < 60 and len(samples) < 2:
        samples.append(r)
    elif 100 < w < 200 and len([s for s in samples if wc(s["fr_text"]) > 60]) < 2:
        samples.append(r)
    elif w > 300 and len([s for s in samples if wc(s["fr_text"]) > 200]) < 1:
        samples.append(r)
    if len(samples) == 5:
        break

print(f"Testing on {len(samples)} footnotes...\n")
print("=" * 80)

MODELS = [
    ("llama-3.3-70b-versatile", "Llama 3.3 70B"),
    ("llama-3.1-8b-instant",    "Llama 3.1 8B Instant"),
]

results = {m[0]: {} for m in MODELS}

for r in samples:
    fid = r["id"]
    fr_text = r["fr_text"]
    fr_wc = wc(fr_text)
    print(f"\n{'─'*60}")
    print(f"Footnote: {fid} | French: {fr_wc} words")
    print(f"FR: {fr_text[:120]}...")
    print()
    for model_id, model_label in MODELS:
        try:
            en = translate(fr_text, model_id)
            en_wc = wc(en)
            ratio = en_wc / fr_wc
            flag = "✅" if ratio >= 0.85 else "⚠️"
            results[model_id][fid] = {"en_wc": en_wc, "ratio": ratio, "text": en}
            print(f"[{model_label}] {en_wc} words | Ratio: {ratio:.2f} {flag}")
            print(f"  {en[:150]}...")
        except Exception as e:
            print(f"[{model_label}] ERROR: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print(f"{'Model':<25} {'Avg Ratio':>10} {'Pass Rate':>10}")
for model_id, model_label in MODELS:
    res = results[model_id]
    if res:
        ratios = [v["ratio"] for v in res.values()]
        avg = sum(ratios) / len(ratios)
        passes = sum(1 for r in ratios if r >= 0.85)
        print(f"{model_label:<25} {avg:>10.2f} {passes}/{len(ratios):>8}")
