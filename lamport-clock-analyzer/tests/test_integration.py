import tempfile
from pathlib import Path
from lamport_clock_analyzer.parser import parse
from lamport_clock_analyzer.analyzer import build_graph

def test_end_to_end():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
        f.write('{"lamport":1,"process":"x"}\n{"lamport":2,"process":"x"}\n')
        path = Path(f.name)
    events = list(parse(path))
    g = build_graph(events)
    assert len(g.edges) >= 1