import json
from heap_snapshot_diff.parser import load_snapshot

def test_load(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps([{"type": "list", "size": 100, "count": 1}]))
    assert "list" in load_snapshot(str(p))