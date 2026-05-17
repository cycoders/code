from latency_budget_allocator.validator import validate_against_traces

def test_no_violations():
    budgets = [{'service': 'api', 'budget_ms': 50}]
    traces = [{'hops': [{'latency_ms': 30}]}]
    result = validate_against_traces(budgets, traces)
    assert result['violations'] == 0