from benchstat_cli.stats import compare

def test_detect_change():
    r1 = {'benchmarks': [{'name': 'x', 'ns_per_op': 100}]}
    r2 = {'benchmarks': [{'name': 'x', 'ns_per_op': 112}]}
    out = compare([r1, r2], 0.05)
    assert '12.0%' in out