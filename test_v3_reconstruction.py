
import json
import copy
from munk_pipeline_v3 import inject_translation

def test_reconstruction():
    original = {
        "text": {
            "Part 1": ["French 1", "French 2"],
            "Intro": {"key": "Value"}
        }
    }
    
    translated_map = {
        "root.text.Part 1.0": "English 1",
        "root.text.Part 1.1": "English 2",
        "root.text.Intro.key": "Translated Value"
    }
    
    reconstructed = copy.deepcopy(original)
    for path, text in translated_map.items():
        inject_translation(reconstructed, path, text)
        
    print(f"Reconstructed: {reconstructed}")
    assert reconstructed["text"]["Part 1"][0] == "English 1"
    assert reconstructed["text"]["Part 1"][1] == "English 2"
    assert reconstructed["text"]["Intro"]["key"] == "Translated Value"
    print("test_reconstruction passed!")

if __name__ == "__main__":
    test_reconstruction()
