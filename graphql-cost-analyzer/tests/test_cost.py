import pytest
from graphql_cost_analyzer.cost import CostConfig, compute_cost

def test_basic_cost():
    assert compute_cost(None, None, CostConfig()) > 0

def test_depth_limit():
    cfg = CostConfig(max_depth=2)
    assert compute_cost(None, None, cfg, depth=5) == float("inf")

def test_list_multiplier():
    cfg = CostConfig(list_multiplier=5.0)
    assert compute_cost(None, None, cfg) >= 1.0