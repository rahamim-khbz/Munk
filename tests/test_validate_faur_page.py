import pytest
from scripts.validate_faur_page import validate_page_record

def test_valid_page_record_passes():
    record = {
        "page_id": "ix",
        "section_file": "00_front_matter.md",
        "spread_index": 4,
        "spread_side": "right",
        "scan_image": "data/faur_scans/page_ix.png",
        "note_pages": ["183"],
        "note_scan_images": ["data/faur_scans/page_183.png"],
        "status": "visual_verified",
        "continues_from_prev_page": False,
        "ends_with_hyphen": False,
        "blocks": [
            {
                "block_id": "pix_b1",
                "type": "heading",
                "level": 2,
                "markdown": "Preface"
            },
            {
                "block_id": "pix_b2",
                "type": "paragraph",
                "indent": "first_para",
                "markdown": "A basic thesis of this work is that *Dalālat al-Ḥā’irīn* is esoteric.[^1] See the diagram knowledge → silence.[^2]"
            }
        ],
        "footnotes": {
            "1": "See José Faur, *Golden Doves with Silver Dots* (Bloomington: Indiana Univ. Press, 1986), xxvi, 63–64.",
            "2": "Werner Jaeger, *Aristotle* (Oxford: Oxford Univ. Press, 1962), 370."
        },
        "audit_log": []
    }
    errors = validate_page_record(record)
    assert errors == []

def test_catches_footnote_mismatch_and_ocr_corruptions():
    bad_record = {
        "page_id": "20",
        "section_file": "02_part_one_apophasis.md",
        "spread_index": 18,
        "spread_side": "left",
        "scan_image": "data/faur_scans/page_020.png",
        "note_pages": ["192"],
        "note_scan_images": ["data/faur_scans/page_192.png"],
        "status": "draft",
        "continues_from_prev_page": False,
        "ends_with_hyphen": False,
        "blocks": [
            {
                "block_id": "p20_b1",
                "type": "paragraph",
                "indent": "indented",
                "markdown": "This has broken hyphen- ation and mangled footnote.\"º Also [^1] and [^2] with year I982 and Cyrillic по."
            }
        ],
        "footnotes": {
            "1": "See Hagiga I3b and 'Aboda Zara x7b."
        },
        "audit_log": []
    }
    errors = validate_page_record(bad_record)
    assert any("Missing footnote definition for [^2]" in e for e in errors)
    assert any("Unhealed mid-line hyphenation" in e for e in errors)
    assert any("Mangled OCR footnote symbol" in e for e in errors)
    assert any("Optical digit/letter confusion" in e for e in errors)
    assert any("Cyrillic character" in e for e in errors)
