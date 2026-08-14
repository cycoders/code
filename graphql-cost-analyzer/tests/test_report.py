from graphql_cost_analyzer.report import render_table

def test_render():
    table = render_table([{"field": "user", "cost": 5}])
    assert "Cost Report" in str(table)