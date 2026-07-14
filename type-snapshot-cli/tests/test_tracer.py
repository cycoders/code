from pathlib import Path
from type_snapshot_cli.tracer import SnapshotTracer

def test_tracer_init():
    t = SnapshotTracer(Path("."))
    assert t.root.exists()