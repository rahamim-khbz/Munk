import os
import pytest

def test_subagent_prompts_exist():
    assert os.path.exists("docs/prompts/munk_translator_prompt.md"), "munk_translator_prompt.md must exist"
    assert os.path.exists("docs/prompts/munk_verifier_prompt.md"), "munk_verifier_prompt.md must exist"

def test_translator_prompt_contains_mandatory_instructions():
    content = open("docs/prompts/munk_translator_prompt.md", "r", encoding="utf-8").read()
    required = [
        "munk-translator",
        "Just Leave It",
        "v2_style_sheet.md",
        "data/reviews/",
        "data/packets/"
    ]
    for r in required:
        assert r in content, f"Missing required term: {r}"

def test_verifier_prompt_contains_mandatory_instructions():
    content = open("docs/prompts/munk_verifier_prompt.md", "r", encoding="utf-8").read()
    required = [
        "munk-verifier",
        "data/reviews/",
        "data/packets/"
    ]
    for r in required:
        assert r in content, f"Missing required term: {r}"
