from scripts.compile_faur_markdown import stitch_pages_to_markdown

def test_stitches_hyphenated_and_continuing_paragraphs_and_appends_footnotes():
    pages = [
        {
            "page_id": "ix",
            "section_file": "00_front_matter.md",
            "continues_from_prev_page": False,
            "ends_with_hyphen": True,
            "blocks": [
                {"block_id": "pix_b1", "type": "heading", "level": 2, "markdown": "Preface"},
                {"block_id": "pix_b2", "type": "paragraph", "indent": "first_para", "markdown": "First complete paragraph.[^1]"},
                {"block_id": "pix_b3", "type": "paragraph", "indent": "indented", "markdown": "Second paragraph ends with knowl-"}
            ],
            "footnotes": {"1": "Note one text."}
        },
        {
            "page_id": "x",
            "section_file": "00_front_matter.md",
            "continues_from_prev_page": True,
            "ends_with_hyphen": False,
            "blocks": [
                {"block_id": "px_b1", "type": "paragraph", "indent": "continuation", "markdown": "edge of the text.[^2]"},
                {"block_id": "px_b2", "type": "blockquote", "markdown": "Indented quote on page x."}
            ],
            "footnotes": {"2": "Note two text."}
        }
    ]
    md = stitch_pages_to_markdown("Preface", pages)
    assert "Second paragraph ends with knowledge of the text.[^2]" in md
    assert "> Indented quote on page x." in md
    assert "[^1]: Note one text." in md
    assert "[^2]: Note two text." in md
    assert "<!--" not in md
