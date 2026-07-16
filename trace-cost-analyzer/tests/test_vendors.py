import tempfile
from trace_cost_analyzer.analyzer import analyze_traces

def test_vendor_pricing():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{}')
        f.flush()
        res = analyze_traces(f.name, 'newrelic', None)
        assert 'estimated_monthly_usd' in res
        Path(f.name).unlink()