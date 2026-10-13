import os
import re

def test_style_sheet_exists():
    path = "docs/plans/v2_style_sheet.md"
    assert os.path.exists(path), "v2_style_sheet.md must exist"

def test_style_sheet_contains_mandatory_sections():
    content = open("docs/plans/v2_style_sheet.md", "r", encoding="utf-8").read()
    required = [
        "Transliteration Standards",
        "Mandatory Terminology Lexicon",
        "Archaism Ban List",
        "Scriptural Citation Standard ('Just Leave It')",
        "Translation Scope and Scholarly Revision",
        "Footnote Formatting Rules"
    ]
    for section in required:
        assert section in content, f"Missing section: {section}"
