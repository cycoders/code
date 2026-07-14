import tempfile
from pathlib import Path
from type_snapshot_cli.aggregator import TypeAggregator

def test_end_to_end():
    agg = TypeAggregator()
    def sample(a, b): pass
    agg.observe(sample, {"a": 1, "b": 2.0})
    agg.observe(sample, {"a": 3, "b": 4.0})
    hints = agg.reduce()
    assert len(hints) == 2