from pathlib import Path
import tempfile
from lamport_clock_analyzer.parser import parse

def test_parse_ndjson():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
        f.write('{"lamport":1,"process":"a"}\n')
        path = Path(f.name)
    events = list(parse(path))
    assert len(events) == 1
    assert events[0].ts == 1