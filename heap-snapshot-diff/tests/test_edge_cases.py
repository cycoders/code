from heap_snapshot_diff.analyzer import diff_snapshots
import json, tempfile

def test_zero_division(tmp_path):
    before = tmp_path / "b.json"
    after = tmp_path / "a.json"
    before.write_text("[]")
    after.write_text(json.dumps([{"type": "int", "size": 8, "count": 1}]))
    res = diff_snapshots(str(before), str(after), 0.01)
    assert res[0]["growth"] == 8.0