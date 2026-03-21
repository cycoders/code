from k8s_cost_estimator_cli.pricing_data import get_prices, Pricing


def test_pricing_lookup():
    p = get_prices("aws", "us-east-1")
    assert isinstance(p, Pricing)
    assert p.cpu_per_core_hour == 0.02496


def test_missing_region_raises():
    import pytest
    with pytest.raises(ValueError):
        get_prices("aws", "unknown")
