import pytest
from latency_budget_allocator.allocator import allocate_budgets

def test_basic_allocation():
    graph = {'api': {}, 'db': {}}
    result = allocate_budgets(graph, 200.0)
    assert len(result) == 2
    assert all(b.budget_ms > 0 for b in result)

def test_allocation_respects_slo():
    graph = {'a': {}, 'b': {}}
    result = allocate_budgets(graph, 100.0)
    assert sum(b.budget_ms for b in result) <= 100.0