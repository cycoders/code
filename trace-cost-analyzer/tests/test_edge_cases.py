from trace_cost_analyzer.analyzer import analyze_traces
import tempfile

def test_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('')
        f.flush()
        res = analyze_traces(f.name, 'datadog', None)
        assert res['spans'] == 0
        Path(f.name).unlink()