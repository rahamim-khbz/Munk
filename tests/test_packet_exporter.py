import os
import json
import re
from scripts.export_packet import export_shard_packet

def test_export_shard_packet_bundles_text_and_footnotes():
    out_dir = "/tmp/test_shards"
    os.makedirs(out_dir, exist_ok=True)
    packet_path = export_shard_packet("p1_w0_s1", ["Part 1, Chapter 22"], out_dir)
    assert os.path.exists(packet_path)
    data = json.load(open(packet_path))
    assert "shard_id" in data
    assert "segments" in data
    assert "footnotes" in data
    assert len(data["segments"]) > 0
    # Every footnote referenced in segments must be present in packet['footnotes']
    referenced_fns = set()
    for seg in data["segments"]:
        referenced_fns.update(re.findall(r'\[\[fn:(\d+)\]\]', seg["english_v1"]))
    for fid in referenced_fns:
        assert f"fn.{fid}" in data["footnotes"] or fid in data["footnotes"]

def test_export_shard_matrix_lookup():
    out_dir = "/tmp/test_shards"
    os.makedirs(out_dir, exist_ok=True)
    packet_path = export_shard_packet("p1_w0_s1", output_dir=out_dir)
    assert os.path.exists(packet_path)
    data = json.load(open(packet_path))
    assert data["shard_id"] == "p1_w0_s1"
    # Should include chapters 22 through 26
    chapter_names = {seg["chapter_id"] for seg in data["segments"]}
    assert "Part 1, Chapter 22" in chapter_names
    assert "Part 1, Chapter 26" in chapter_names
