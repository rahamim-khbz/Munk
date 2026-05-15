import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MAKBILI_HE_PATH = "/Users/rayhabbaz/Downloads/Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json"
MUNK_EN_PATH = "/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide/test_translations_threaded.json"

def get_maqbili_he():
    with open(MAKBILI_HE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_munk_en_refs():
    with open(MUNK_EN_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return list(data['segments'].keys())

def translate_maqbili():
    maqbili_data = get_maqbili_he()
    munk_refs = get_munk_en_refs()
    
    # We want to translate the Hebrew segments to match the Munk refs
    # Sections of interest:
    # "Letter to R Joseph son of Judah"
    # "Prefatory Remarks"
    
    letter_he = maqbili_data['text']['Letter to R Joseph son of Judah']
    prefatory_he = maqbili_data['text']['Prefatory Remarks']
    
    prompt = f"""
    You are an expert translator of medieval Jewish philosophy.
    I have a Hebrew edition of Maimonides' 'Guide for the Perplexed' (Maqbili Edition).
    I need you to translate specific sections into English, aligning them EXACTLY with the segment boundaries used in a reference English translation (Munk).
    
    MAQBILI HEBREW TEXT (Letter to R Joseph):
    {json.dumps(letter_he, ensure_ascii=False)}
    
    MAQBILI HEBREW TEXT (Prefatory Remarks):
    {json.dumps(prefatory_he, ensure_ascii=False)}
    
    REFERENCE MUNK SEGMENT IDs (that you must output for):
    {json.dumps([ref for ref in munk_refs if 'Letter' in ref or 'Prefatory' in ref])}
    
    Return a JSON object where each key is a Munk Segment ID and the value is the English translation of the corresponding Maqbili Hebrew.
    Ensure the English style is modern yet academic (Maqbili-style), reflecting the clarity of the 2024 Hebrew edition.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "translation": {"type": "string"}
                            },
                            "required": ["id", "translation"]
                        }
                    }
                },
                "required": ["segments"]
            }
        )
    )
    
    with open("/Users/rayhabbaz/Munk's Guide/maqbili_english.json", 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("Successfully created maqbili_english.json")

if __name__ == "__main__":
    translate_maqbili()
