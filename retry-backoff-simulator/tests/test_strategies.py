import random
import pytest
from unittest.mock import patch

from retry_backoff_simulator.strategies import (
    FixedStrategy,
    ExponentialStrategy,
    FullJitterStrategy,
    EqualJitterStrategy,
    DecorrelatedJitterStrategy,
)


@pytest.fixture
def base_config():
    return {"base_delay": 0.1, "max_delay": 10.0, "factor": 2.0}


class TestFixedStrategy:
    def test_fixed_delays(self, base_config):
        strat = FixedStrategy(**base_config)
        assert strat.next_delay(1) == 0.1
        assert strat.next_delay(5) == 0.1


class TestExponentialStrategy:
    def test_exponential_growth(self, base_config):
        strat = ExponentialStrategy(**base_config)
        assert strat.next_delay(1) == 0.1
        assert strat.next_delay(2) == 0.2
        assert strat.next_delay(4) == 0.8
        assert strat.next_delay(5) == 1.6
        assert strat.next_delay(10) == 10.0  # capped


class TestFullJitterStrategy:
    @patch("random.random")
    def test_full_jitter_range(self, mock_rand, base_config):
        mock_rand.return_value = 0.5
        strat = FullJitterStrategy(**base_config)
        cap1 = 0.1
        assert 0.0 <= strat.next_delay(1) <= cap1
        cap5 = min(0.1 * (2 ** 4), 10.0)
        assert 0.0 <= strat.next_delay(5) <= cap5


class TestEqualJitterStrategy:
    @patch("random.uniform")
    def test_equal_jitter_range(self, mock_uniform, base_config):
        mock_uniform.return_value = 0.75
        strat = EqualJitterStrategy(**base_config)
        cap1 = 0.1
        lower1 = cap1 / 2
        delay1 = strat.next_delay(1)
        assert lower1 <= delay1 <= cap1


class TestDecorrelatedJitterStrategy:
    @patch("random.uniform")
    def test_decorrelated_stateful(self, mock_uniform, base_config):
        mock_uniform.side_effect = [0.15, 0.4, 0.8]  # controlled
        strat = DecorrelatedJitterStrategy(**base_config)
        assert 0.1 <= strat.next_delay(1) <= 0.3  # first ~base
        d2 = strat.next_delay(2)
        assert 0.1 <= d2 <= min(10, 0.3 * 3)
        d3 = strat.next_delay(3)
        assert 0.1 <= d3 <= min(10, d2 * 3)
