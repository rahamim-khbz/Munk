import json
import os

def test_preface_vol3_structure():
    assert os.path.exists("preface_vol3.json"), "preface_vol3.json does not exist"
    
    with open("preface_vol3.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "fr" in data, "Missing 'fr' key"
    assert "en" in data, "Missing 'en' key"
    assert len(data["fr"]) == 14, f"Expected 14 French segments, got {len(data['fr'])}"
    assert len(data["en"]) == 14, f"Expected 14 English segments, got {len(data['en'])}"
    
    fn_dict = data.get("footnotes_en", {})
    assert "3007" in fn_dict, "Missing footnote 3007"
    assert "3008" in fn_dict, "Missing footnote 3008"
    
    print("test_preface_vol3 passed successfully!")

if __name__ == "__main__":
    test_preface_vol3_structure()
