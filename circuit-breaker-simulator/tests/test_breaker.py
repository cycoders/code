import time
import pytest
from circuit_breaker_simulator.breaker import ConsecutiveBreaker, ThresholdBreaker, create_breaker
from circuit_breaker_simulator.models import BreakerConfig

@pytest.fixture
def consec_config():
    return BreakerConfig(name="test", type="consecutive", consec_threshold=3, timeout_secs=1)

@pytest.fixture
def thresh_config():
    return BreakerConfig(name="test", type="threshold", failure_threshold=3, window_secs=10, timeout_secs=1)

class TestConsecutiveBreaker:
    def test_allow_closed(self, consec_config):
        b = ConsecutiveBreaker("test", consec_config)
        assert b.allow() is True

    def test_open_after_threshold(self, consec_config):
        b = ConsecutiveBreaker("test", consec_config)
        for _ in range(2):
            b.on_result(False)
            assert b.allow()
        b.on_result(False)  # 3rd fail
        assert not b.allow()

    def test_reset_on_success(self, consec_config):
        b = ConsecutiveBreaker("test", consec_config)
        b.on_result(False)
        b.on_result(False)
        b.on_result(True)
        assert b.allow()

    def test_timeout_recovery(self, consec_config):
        b = ConsecutiveBreaker("test", consec_config)
        for _ in range(3):
            b.on_result(False)
        time.sleep(1.1)  # > timeout
        assert b.allow()

class TestThresholdBreaker:
    def test_allow_closed(self, thresh_config):
        b = ThresholdBreaker("test", thresh_config)
        assert b.allow()

    def test_open_after_threshold(self, thresh_config):
        b = ThresholdBreaker("test", thresh_config)
        for _ in range(3):
            b.on_result(False)
        assert not b.allow()

    def test_window_respects_time(self, thresh_config):
        b = ThresholdBreaker("test", thresh_config)
        for _ in range(3):
            b.on_result(False)
        time.sleep(11)  # > window
        assert len(b.failure_times) == 0  # maxlen approx
        assert b.allow()

    def test_timeout(self, thresh_config):
        b = ThresholdBreaker("test", thresh_config)
        for _ in range(3):
            b.on_result(False)
        time.sleep(1.1)
        assert b.allow()

@pytest.mark.parametrize("btype,cfg", [("consecutive", {"consec_threshold":3}), ("threshold", {"failure_threshold":3})])
def test_factory(btype, cfg):
    config = BreakerConfig(name="f", type=btype, **cfg)
    b = create_breaker("f", config)
    assert b.name == "f"
