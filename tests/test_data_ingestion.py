import os
import sys
import json

def test_ingestion():
    # Verify local file presence
    assert os.path.exists("French.json"), "French.json missing"
    assert os.path.exists("Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json"), "Judeo-Arabic JSON missing"
    
    tibon_local = "Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json"
    assert os.path.exists(tibon_local), "Ibn Tibon JSON missing locally"
    
    # Load build script context safely
    sys.path.insert(0, os.path.abspath("."))
    import build_full_viewer
    
    # Assert dictionaries are exposed
    assert hasattr(build_full_viewer, "french_main"), "build_full_viewer missing french_main dict"
    assert hasattr(build_full_viewer, "jrb_main"), "build_full_viewer missing jrb_main dict"
    assert hasattr(build_full_viewer, "tibon_main"), "build_full_viewer missing tibon_main dict"
    
    # Assert variant text resolver exists and works
    assert hasattr(build_full_viewer, "get_variant_text"), "build_full_viewer missing get_variant_text resolver"
    
    # Let's verify a lookup from French.json
    # e.g. root.text.Part 1.Introduction.0
    text_fr = build_full_viewer.get_variant_text(build_full_viewer.french_main, "root.text.Part 1.Introduction.0")
    assert text_fr and "OBSERVATION" in text_fr, f"Failed to retrieve valid French variant text, got: {text_fr}"
    
    print("Ingestion verification suite passed successfully.")

if __name__ == "__main__":
    test_ingestion()
