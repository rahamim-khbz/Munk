import pytest
from scripts.validate_review import StrictApparatusValidator

def test_detects_untranslated_french():
    v = StrictApparatusValidator()
    text = "He said: <i>Touche les montagnes, et qu’elles fument</i>."
    ok, errs = v.validate_segment("seg.1", "He said: touch.", text, [])
    assert not ok
    assert any("french_detected" in e for e in errs)

def test_detects_inverted_rtl_span():
    v = StrictApparatusValidator()
    text = "And she took <span dir=\"rtl\">her pitcher</span>."
    ok, errs = v.validate_segment("seg.2", "original", text, [])
    assert not ok
    assert any("invalid_rtl_content" in e for e in errs)

def test_detects_dropped_footnote_marker():
    v = StrictApparatusValidator()
    orig = "Word[[fn:10]] and more[[fn:11]]."
    rev = "Word and more[[fn:11]]."
    ok, errs = v.validate_segment("seg.3", orig, rev, ["fn:10", "fn:11"])
    assert not ok
    assert any("footnote_marker_mismatch" in e for e in errs)

def test_detects_archaisms():
    v = StrictApparatusValidator()
    text = "Thou shalt not go unto them whilst they speak."
    ok, errs = v.validate_segment("seg.4", "Don't go.", text, [])
    assert not ok
    assert any("archaism_detected" in e for e in errs)

def test_detects_unclosed_html_tags():
    v = StrictApparatusValidator()
    text = "This is <i>italic but unclosed."
    ok, errs = v.validate_segment("seg.5", "orig", text, [])
    assert not ok
    assert any("unclosed_html_tag" in e for e in errs)

def test_passes_valid_text():
    v = StrictApparatusValidator()
    orig = "The term <span dir=\"rtl\">אלוהים</span> is equivocal[[fn:1]]."
    rev = "The term <span dir=\"rtl\">אלוהים</span> is an equivocal term[[fn:1]]."
    ok, errs = v.validate_segment("seg.6", orig, rev, ["fn:1"])
    assert ok
    assert len(errs) == 0
