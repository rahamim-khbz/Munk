from scripts.prepare_faur_pages import build_book_page_manifest

def test_manifest_maps_preface_and_part_one_correctly():
    manifest = build_book_page_manifest()
    by_id = {entry["page_id"]: entry for entry in manifest}
    assert "ix" in by_id
    assert by_id["ix"]["spread_index"] == 4
    assert by_id["ix"]["spread_side"] == "right"
    assert by_id["ix"]["section_file"] == "00_front_matter.md"
    assert "183" in by_id["ix"]["note_pages"]

    assert "20" in by_id
    assert by_id["20"]["spread_index"] == 18
    assert by_id["20"]["spread_side"] == "left"
    assert by_id["20"]["section_file"] == "02_part_one_apophasis.md"
