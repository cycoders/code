from heap_snapshot_diff.analyzer import diff_snapshots
import json, tempfile, os

def test_diff(tmp_path):
    before = tmp_path / "b.json"
    after = tmp_path / "a.json"
    before.write_text(json.dumps([{"type": "dict", "size": 100, "count": 1}]))
    after.write_text(json.dumps([{"type": "dict", "size": 300, "count": 3}]))
    res = diff_snapshots(str(before), str(after), 0.1)
    assert res[0]["growth"] > 1.9