import json
import pytest
from scripts.faur_queue_runner import load_queue_state, get_next_pending_page, mark_page_status

def test_queue_lifecycle(tmp_path):
    q_file = str(tmp_path / "queue.json")
    state = load_queue_state(q_file)
    assert state["status"] == "ready"
    assert "ix" in state["active_batch_pages"]
    
    nxt = get_next_pending_page(state)
    assert nxt == "ix"
    
    mark_page_status(state, "ix", "visual_verified", q_file)
    reloaded = load_queue_state(q_file)
    assert reloaded["pages"]["ix"]["status"] == "visual_verified"
    assert get_next_pending_page(reloaded) == "x"
