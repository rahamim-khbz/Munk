import json
import re
import pytest
from scripts.validate_review import StrictApparatusValidator

def test_chapters_1_21_segments_and_footnotes_valid():
    v2 = json.load(open("munk_production_v2.json", "r", encoding="utf-8"))
    validator = StrictApparatusValidator()
    
    reviewed_segs = v2["metadata"]["reviewed_segments"]
    assert len(reviewed_segs) == 144, f"Expected 144 reviewed segments, found {len(reviewed_segs)}"

    ref_fns = set()
    for sid in reviewed_segs:
        text = v2["text"][sid]
        ok, errs = validator.validate_segment(sid, text, text)
        assert ok, f"Segment validation error on {sid}: {errs}"
        ref_fns.update(re.findall(r'\[\[fn:(\d+)\]\]', text))

    reviewed_fns = v2["metadata"]["reviewed_footnotes"]
    assert len(reviewed_fns) >= 173, f"Expected at least 173 reviewed footnotes, found {len(reviewed_fns)}"

    for fn_num in sorted(ref_fns, key=lambda x: int(x)):
        fid = f"fn.{fn_num}"
        fn_text = v2["footnotes"][fid]
        ok, errs = validator.validate_footnote(fid, fn_text, fn_text)
        assert ok, f"Footnote validation error on {fid}: {errs}"
