from heap_snapshot_diff.analyzer import diff_snapshots
print(diff_snapshots("before.json", "after.json", 0.05))