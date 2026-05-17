def validate_against_traces(budgets: list, traces: list[dict]) -> dict:
    """Check historical traces against allocated budgets."""
    violations = []
    for trace in traces:
        for hop in trace.get('hops', []):
            if hop['latency_ms'] > budgets[0].budget_ms:  # simplified
                violations.append(hop)
    return {'violations': len(violations), 'total_traces': len(traces)}