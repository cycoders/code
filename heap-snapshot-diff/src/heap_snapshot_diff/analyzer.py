from heap_snapshot_diff.parser import load_snapshot

def diff_snapshots(before_path: str, after_path: str, threshold: float):
    before = load_snapshot(before_path)
    after = load_snapshot(after_path)
    diffs = []
    for typ, a in after.items():
        b = before.get(typ, {"size": 0, "count": 0})
        growth = (a["size"] - b["size"]) / max(b["size"], 1)
        if growth >= threshold:
            diffs.append({"type": typ, "growth": growth, "delta_bytes": a["size"] - b["size"]})
    return sorted(diffs, key=lambda x: -x["growth"])