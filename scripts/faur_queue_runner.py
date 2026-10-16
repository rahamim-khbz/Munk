#!/usr/bin/env python3
"""
Long-timescale queue orchestrator for José Faur's Homo Mysticus page-by-page transcription.
Reads data/faur_queue_state.json, identifies the next pending page in the active batch,
checks for human feedback/redlines, and coordinates the transcription and audit lifecycle.
"""

import json
import os
import subprocess
import sys
from typing import Dict, Any, Optional

QUEUE_PATH = "data/faur_queue_state.json"
FEEDBACK_PATH = "data/faur_review_feedback.json"
PAGES_DIR = "data/faur_pages"


def load_queue_state(queue_path: str = QUEUE_PATH) -> Dict[str, Any]:
    if not os.path.exists(queue_path):
        from scripts.prepare_faur_pages import build_book_page_manifest
        manifest = build_book_page_manifest()
        state = {
            "active_batch_name": "pilot_preface_ix_to_xiii",
            "active_batch_pages": ["ix", "x", "xi", "xii", "xiii"],
            "pause_at_batch_end": True,
            "status": "ready",
            "pages": {
                item["page_id"]: {
                    "status": "pending",
                    "section_file": item["section_file"],
                    "spread_index": item["spread_index"],
                    "spread_side": item["spread_side"],
                    "scan_image": item["scan_image"],
                    "note_pages": item["note_pages"],
                }
                for item in manifest if item["section_file"] != "06_notes.md"
            }
        }
        os.makedirs(os.path.dirname(queue_path), exist_ok=True)
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return state

    with open(queue_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue_state(state: Dict[str, Any], queue_path: str = QUEUE_PATH):
    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_next_pending_page(state: Dict[str, Any]) -> Optional[str]:
    active_pages = state.get("active_batch_pages", [])
    for pid in active_pages:
        page_info = state.get("pages", {}).get(pid, {})
        if page_info.get("status") in ("pending", "in_progress", "failed"):
            return pid
    return None


def check_unresolved_redlines(feedback_path: str = FEEDBACK_PATH) -> list[str]:
    if not os.path.exists(feedback_path):
        return []
    try:
        with open(feedback_path, "r", encoding="utf-8") as f:
            feedback = json.load(f)
        return [pid for pid, data in feedback.items() if data.get("status") == "redlined"]
    except Exception:
        return []


def mark_page_status(state: Dict[str, Any], page_id: str, status: str, queue_path: str = QUEUE_PATH):
    if page_id in state.get("pages", {}):
        state["pages"][page_id]["status"] = status
    save_queue_state(state, queue_path)


def main():
    state = load_queue_state()
    redlined = check_unresolved_redlines()
    if redlined:
        print(f"PAUSE: Unresolved user redlines on page(s): {', '.join(redlined)}. Halting queue until addressed.")
        state["status"] = "awaiting_human_review"
        save_queue_state(state)
        sys.exit(0)

    next_page = get_next_pending_page(state)
    if not next_page:
        print("Active batch complete! Queue status: awaiting_human_review.")
        state["status"] = "awaiting_human_review"
        save_queue_state(state)
        sys.exit(0)

    print(f"NEXT_PAGE_READY: {next_page}")


if __name__ == "__main__":
    main()
