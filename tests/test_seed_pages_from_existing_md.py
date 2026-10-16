from scripts.seed_pages_from_existing_md import slice_md_by_page_anchors, convert_unicode_superscripts_to_fn

def test_slice_md_by_page_anchors_extracts_pages_and_converts_superscripts():
    sample_md = """# Introduction

---

<!-- [p. 1] -->

First paragraph with unicode note.¹

> Blockquote on page one.²

<!-- [p. 2] -->
continuation of sentence on page two.³
"""
    sliced = slice_md_by_page_anchors(sample_md)
    assert "1" in sliced
    assert "2" in sliced
    p1_blocks = sliced["1"]["blocks"]
    assert len(p1_blocks) == 2
    assert p1_blocks[0]["markdown"] == "First paragraph with unicode note.[^1]"
    assert p1_blocks[1]["type"] == "blockquote"
    assert p1_blocks[1]["markdown"] == "Blockquote on page one.[^2]"
    assert sliced["2"]["continues_from_prev_page"] is True
