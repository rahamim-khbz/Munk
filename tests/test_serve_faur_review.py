import json
import pytest
from scripts.serve_faur_review import ReviewServerHandler

def test_load_page_and_save_feedback(tmp_path):
    # Test reading page json and saving review feedback to disk
    feedback_file = tmp_path / "faur_review_feedback.json"
    feedback_data = {
        "page_id": "ix",
        "redlines": [
            {
                "target_text": "knowl-",
                "replacement_text": "knowledge",
                "comment": "Healed line wrap"
            }
        ],
        "status": "redlined"
    }
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump({"ix": feedback_data}, f)
    
    with open(feedback_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert "ix" in loaded
    assert loaded["ix"]["status"] == "redlined"
    assert loaded["ix"]["redlines"][0]["replacement_text"] == "knowledge"
