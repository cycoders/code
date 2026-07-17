from flamegraph_diff_cli.diff import compute_diff

def test_detects_regression():
    before = {'main;hot': 100}
    after = {'main;hot': 300}
    res = compute_diff(before, after, 0.05)
    assert len(res.regressions) == 1
    assert res.regressions[0]['delta'] == 200