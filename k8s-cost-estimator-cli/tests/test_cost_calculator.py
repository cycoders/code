import pytest
from k8s_cost_estimator_cli.cost_calculator import calculate_costs
from k8s_cost_estimator_cli.types import Config


def test_cost_calc(sample_deployment):
    cfg = Config("aws", "us-east-1", 3, 1.0, 30)
    breakdown = calculate_costs(sample_deployment, cfg)
    assert breakdown.total_cost > 0
    assert breakdown.namespace == "default"
