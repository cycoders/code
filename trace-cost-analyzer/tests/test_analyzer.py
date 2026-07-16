import tempfile
from pathlib import Path
from trace_cost_analyzer.analyzer import analyze_traces

def test_basic_count():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"traceId":"1"}\n' * 1000)
        f.flush()
        res = analyze_traces(f.name, 'honeycomb', None)
        assert res['spans'] == 1000
        Path(f.name).unlink()