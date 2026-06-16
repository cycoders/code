from query_plan_diff_cli.diff import diff_plans

def test_identical_plans():
    d = diff_plans('base.json', 'head.json', None)
    assert d.cost_delta == 0.0