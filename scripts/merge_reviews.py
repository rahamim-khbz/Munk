#!/usr/bin/env python3
"""
scripts/merge_reviews.py - Atomic Single-Writer Merge Engine.
Ensures zero data races by acquiring a file lock, running StrictApparatusValidator,
updating text/footnotes atomically via temp file rename, and recording markdown audits.
"""

import os
import sys
import json
import fcntl
import argparse
from typing import Dict, Any, Optional, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.validate_review import StrictApparatusValidator

class ReviewMergeEngine:
    def __init__(
        self,
        v2_path: str = "munk_production_v2.json",
        audit_dir: str = "docs/audits",
        validator: Optional[StrictApparatusValidator] = None
    ):
        self.v2_path = v2_path
        self.audit_dir = audit_dir
        self.validator = validator or StrictApparatusValidator()

    def apply_shard_review(self, review_data: Dict[str, Any]) -> bool:
        """Atomically validates and applies a shard review packet to munk_production_v2.json."""
        lock_path = f"{self.v2_path}.lock"
        os.makedirs(os.path.dirname(os.path.abspath(self.v2_path)) or ".", exist_ok=True)

        with open(lock_path, "w") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                # 1. Load current v2 state
                if not os.path.exists(self.v2_path):
                    v2_data = {
                        "metadata": {"reviewed_segments": [], "reviewed_footnotes": []},
                        "text": {},
                        "footnotes": {}
                    }
                else:
                    with open(self.v2_path, "r", encoding="utf-8") as f:
                        v2_data = json.load(f)

                if "metadata" not in v2_data:
                    v2_data["metadata"] = {}
                v2_data["metadata"].setdefault("reviewed_segments", [])
                v2_data["metadata"].setdefault("reviewed_footnotes", [])
                v2_data.setdefault("text", {})
                v2_data.setdefault("footnotes", {})

                # 2. Pre-validate all segments and footnotes
                segments_review = review_data.get("segments", {})
                footnotes_review = review_data.get("footnotes", {})
                all_errors = []

                for seg_id, seg_entry in segments_review.items():
                    status = seg_entry.get("status", "UNCHANGED")
                    if status == "MODIFIED":
                        orig_text = v2_data["text"].get(seg_id, "")
                        rev_text = seg_entry.get("revised_text", "")
                        ok, errs = self.validator.validate_segment(seg_id, orig_text, rev_text)
                        if not ok:
                            all_errors.extend(errs)

                for fn_id, fn_entry in footnotes_review.items():
                    status = fn_entry.get("status", "UNCHANGED")
                    if status == "MODIFIED":
                        orig_fn = v2_data["footnotes"].get(fn_id, "")
                        rev_fn = fn_entry.get("revised_text", "")
                        ok, errs = self.validator.validate_footnote(fn_id, orig_fn, rev_fn)
                        if not ok:
                            all_errors.extend(errs)

                if all_errors:
                    print(f"Validation failed for shard {review_data.get('shard_id')}:")
                    for err in all_errors:
                        print(f"  - {err}")
                    return False

                # 3. Apply updates
                applied_segs = []
                applied_fns = []

                for seg_id, seg_entry in segments_review.items():
                    status = seg_entry.get("status", "UNCHANGED")
                    if status == "MODIFIED":
                        v2_data["text"][seg_id] = seg_entry["revised_text"]
                        applied_segs.append(seg_id)
                    if seg_id not in v2_data["metadata"]["reviewed_segments"]:
                        v2_data["metadata"]["reviewed_segments"].append(seg_id)

                for fn_id, fn_entry in footnotes_review.items():
                    status = fn_entry.get("status", "UNCHANGED")
                    if status == "MODIFIED":
                        v2_data["footnotes"][fn_id] = fn_entry["revised_text"]
                        applied_fns.append(fn_id)
                    if fn_id not in v2_data["metadata"]["reviewed_footnotes"]:
                        v2_data["metadata"]["reviewed_footnotes"].append(fn_id)

                # 4. Atomic Write
                tmp_path = f"{self.v2_path}.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(v2_data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, self.v2_path)

                # 5. Generate Audit Report
                self._generate_audit(review_data, applied_segs, applied_fns)
                return True
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def _generate_audit(
        self,
        review_data: Dict[str, Any],
        applied_segs: List[str],
        applied_fns: List[str]
    ):
        os.makedirs(self.audit_dir, exist_ok=True)
        shard_id = review_data.get("shard_id", "unknown_shard")
        ch_name = review_data.get("chapter_name", shard_id)
        safe_name = ch_name.replace(" ", "_").replace(",", "").replace("'", "").replace("/", "_")
        audit_file = os.path.join(self.audit_dir, f"review_audit_{safe_name}.md")

        lines = [
            f"# Review Audit: {ch_name}",
            f"- **Shard ID:** `{shard_id}`",
            f"- **Modified Segments:** {len(applied_segs)}",
            f"- **Modified Footnotes:** {len(applied_fns)}",
            "",
            "## Segment Details",
            ""
        ]

        segments_review = review_data.get("segments", {})
        for seg_id in applied_segs:
            info = segments_review.get(seg_id, {})
            lines.append(f"### `{seg_id}`")
            lines.append(f"- **Rationale:** {info.get('rationale', 'N/A')}")
            lines.append(f"- **Flags:** {', '.join(info.get('flags', []))}")
            lines.append(f"- **Revised:**\n> {info.get('revised_text', '')}\n")

        lines.append("## Footnote Details\n")
        footnotes_review = review_data.get("footnotes", {})
        for fn_id in applied_fns:
            info = footnotes_review.get(fn_id, {})
            lines.append(f"### `{fn_id}`")
            lines.append(f"- **Rationale:** {info.get('rationale', 'N/A')}")
            lines.append(f"- **Flags:** {', '.join(info.get('flags', []))}")
            lines.append(f"- **Revised:**\n> {info.get('revised_text', '')}\n")

        with open(audit_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

def main():
    parser = argparse.ArgumentParser(description="Merge Shard Review into munk_production_v2.json")
    parser.add_argument("--review-file", type=str, required=True, help="Path to reviewed shard JSON")
    parser.add_argument("--v2-path", type=str, default="munk_production_v2.json", help="Path to v2 JSON")
    parser.add_argument("--audit-dir", type=str, default="docs/audits", help="Directory for audits")
    args = parser.parse_args()

    with open(args.review_file, "r", encoding="utf-8") as f:
        review_data = json.load(f)

    engine = ReviewMergeEngine(v2_path=args.v2_path, audit_dir=args.audit_dir)
    success = engine.apply_shard_review(review_data)
    if success:
        print(f"Successfully applied review from {args.review_file}")
    else:
        print(f"Failed to apply review from {args.review_file}")
        exit(1)

if __name__ == "__main__":
    main()
