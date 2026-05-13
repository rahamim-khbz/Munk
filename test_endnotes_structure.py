import json
import os

def test_endnotes_files():
    files = ["endnotes_vol1.json", "endnotes_vol2.json", "endnotes_vol3.json"]
    for fn in files:
        assert os.path.exists(fn), f"{fn} does not exist"
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "fr" in data, f"Missing 'fr' key in {fn}"
        assert "en" in data, f"Missing 'en' key in {fn}"
        assert len(data["fr"]) == len(data["en"]), f"Array mismatch in {fn}"
        assert len(data["fr"]) > 0, f"Empty array in {fn}"
        
    print("test_endnotes_structure passed successfully!")

if __name__ == "__main__":
    test_endnotes_files()
