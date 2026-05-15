import json
import re

# Load the current cleaned preface (which has 11 segments, one per page roughly)
with open("preface_cleaned.json", "r", encoding="utf-8") as f:
    preface_segments = json.load(f)

# Merge all into one block
full_text = " ".join(preface_segments)

# Patterns to remove
# 1. Page headers/numbers
# Examples: "ij ' PREFACE.", "PRÉFACE. iij", "ly PREFACE.", "PRÉFACE. V", "VI PREFACE.", "PRÉFACE. Vij", "VllJ PREFACE.", "PRÉFACE. ix", "X PREFACE."
patterns_to_remove = [
    r"[ivxlj]+ ' PREFACE\.",
    r"PRÉFACE\. [ivxlj]+",
    r"[ivxlj]+ PREFACE\.",
    r"PREFACE\. [ivxlj]+",
    r"PREFACE\.",
    r"PRÉFACE\.",
    # Specific page markers found in OCR
    r"\bïj\b", r"\biij\b", r"\bly\b", r"\bVij\b", r"\bVllJ\b", r"\bix\b", 
    r"TABLE DES CHAPITRES\.",
    r"Digitized by the Internet Archive",
    r"http://www.archive.org/details/leguidedesgar01maim",
    r"\bï\b"
]

# Additional manual fixes for common OCR misreads in this specific text
cleaned_text = full_text
for pattern in patterns_to_remove:
    cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)

# Correct the misread "Première" abbreviations
cleaned_text = re.sub(r"P[\^®\*]+\s+partie", "Ire partie", cleaned_text)
cleaned_text = re.sub(r"P[\^®\*]+", "Ire", cleaned_text)
cleaned_text = cleaned_text.replace("ï ", " ")

# Normalize whitespace
cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
print(f"Cleaned text starts with: {cleaned_text[:200]}")

# Paragraph start phrases (french)
para_starts = [
    "L'ouvrage de Maïmonide",
    "Comme véritable fondateur",
    "Mais la haute réputation",
    "En Egypte, où vivait",
    "La célébrité dont jouissait",
    "Je ne dois point ici anticiper",
    "On comprendra aisément",
    "Depuis Buxtorf, le Guide",
    "Depuis plus de vingt ans",
    "J'ai annoncé ce projet",
    "Un voyage que je fis",
    "Me trouvant enfin en possession",
    "La perte totale de la vue",
    "Je dois maintenant rendre",
    "Ce premier volume renferme",
    "On a vu quelles ont été",
    "Cependant, j'ai conservé",
    "Dans la traduction française",
    "Il n'est que trop facile",
    "J'ai accompagné la traduction",
    "Un certain nombre de notes",
    "Je ne puis terminer",
    "J'ai eu à lutter",
    "La gravité de cette mission",
    "S. MUNK."
]

# Split into paragraphs
paragraphs = []
current_text = cleaned_text

for i in range(len(para_starts)):
    start_phrase = para_starts[i]
    if i + 1 < len(para_starts):
        next_phrase = para_starts[i+1]
        # Find start and end
        start_idx = current_text.find(start_phrase)
        end_idx = current_text.find(next_phrase)
        if start_idx != -1 and end_idx != -1:
            paragraphs.append(current_text[start_idx:end_idx].strip())
            current_text = current_text[end_idx:]
    else:
        # Last one
        start_idx = current_text.find(start_phrase)
        if start_idx != -1:
            paragraphs.append(current_text[start_idx:].strip())

# Save to a new file
with open("preface_resegmented.json", "w", encoding="utf-8") as f:
    json.dump(paragraphs, f, ensure_ascii=False, indent=2)

print(f"Resegmented into {len(paragraphs)} paragraphs.")
for i, p in enumerate(paragraphs):
    print(f"Para {i}: {p[:100]}...")
