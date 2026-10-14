import os
import json
import pytest
from scripts.merge_reviews import ReviewMergeEngine

def test_merge_review_updates_v2_and_generates_audit(tmp_path):
    v2_mock = tmp_path / "v2.json"
    audit_mock = tmp_path / "audits"
    v2_mock.write_text(json.dumps({
        "metadata": {"reviewed_segments": [], "reviewed_footnotes": []},
        "text": {"seg.1": "Old text"},
        "footnotes": {"fn.1": "Old note"}
    }))
    engine = ReviewMergeEngine(v2_path=str(v2_mock), audit_dir=str(audit_mock))
    review_data = {
        "shard_id": "test_shard",
        "chapter_name": "Part 1, Chapter 99",
        "segments": {
            "seg.1": {
                "status": "MODIFIED",
                "revised_text": "New text",
                "flags": ["style_modernization"],
                "rationale": "Updated"
            }
        },
        "footnotes": {
            "fn.1": {
                "status": "MODIFIED",
                "revised_text": "New note",
                "flags": ["style_modernization"],
                "rationale": "Updated note"
            }
        }
    }
    success = engine.apply_shard_review(review_data)
    assert success
    saved = json.loads(v2_mock.read_text())
    assert saved["text"]["seg.1"] == "New text"
    assert saved["footnotes"]["fn.1"] == "New note"
    assert "seg.1" in saved["metadata"]["reviewed_segments"]
    assert "fn.1" in saved["metadata"]["reviewed_footnotes"]

    # Verify audit file was generated
    audit_files = list(audit_mock.glob("*.md"))
    assert len(audit_files) > 0

def test_merge_review_rejects_invalid_review(tmp_path):
    v2_mock = tmp_path / "v2.json"
    audit_mock = tmp_path / "audits"
    v2_mock.write_text(json.dumps({
        "metadata": {"reviewed_segments": [], "reviewed_footnotes": []},
        "text": {"seg.1": "Old text[[fn:1]]"},
        "footnotes": {"fn.1": "Old note"}
    }))
    engine = ReviewMergeEngine(v2_path=str(v2_mock), audit_dir=str(audit_mock))
    # Review drops footnote marker [[fn:1]]
    bad_review_data = {
        "shard_id": "bad_shard",
        "chapter_name": "Part 1, Chapter 1",
        "segments": {
            "seg.1": {
                "status": "MODIFIED",
                "revised_text": "New text without marker",
                "flags": ["style_modernization"],
                "rationale": "Dropped marker"
            }
        },
        "footnotes": {}
    }
    success = engine.apply_shard_review(bad_review_data)
    assert not success
    # Verify original file untouched
    saved = json.loads(v2_mock.read_text())
    assert saved["text"]["seg.1"] == "Old text[[fn:1]]"
    assert "seg.1" not in saved["metadata"]["reviewed_segments"]
