import pytest
from datetime import datetime
from ratelimit_simulator.policies import (
    RateLimiter,
    FixedWindow,
    SlidingWindow,
    TokenBucket,
    LeakyBucket,
    Decision,
    create_policy,
)


@pytest.mark.parametrize(
    "policy_cls, params, tests",
    [
        (
            FixedWindow,
            {"limit": 2, "window": 1.0},
            [
                ("user1", 0.0, True),
                ("user1", 0.0, True),
                ("user1", 0.0, False),
                ("user1", 1.1, True),
            ],
        ),
        (
            SlidingWindow,
            {"limit": 2, "window": 1.0},
            [
                ("user1", 0.0, True),
                ("user1", 0.5, True),
                ("user1", 0.6, False),  # 0.0 and 0.5 still in window
                ("user1", 1.6, True),  # old pruned
            ],
        ),
        (
            TokenBucket,
            {"capacity": 2.0, "refill_rate": 1.0},
            [
                ("user1", 0.0, True),
                ("user1", 0.0, True),
                ("user1", 0.0, False),
                ("user1", 1.1, True),  # refilled ~1
            ],
        ),
        (
            LeakyBucket,
            {"capacity": 2, "leak_rate": 1.0},
            [
                ("user1", 0.0, True),
                ("user1", 0.0, True),
                ("user1", 0.0, False),
                ("user1", 1.1, True),  # leaked 1.1
            ],
        ),
    ],
)
async def test_policies(policy_cls, params, tests):
    policy = policy_cls(**params)
    for key, now, expected_allowed in tests:
        decision = policy.is_allowed(key, now)
        assert decision.allowed == expected_allowed


@pytest.mark.parametrize("name", ["fixed", "sliding", "token", "leaky"])
def test_create_policy(name):
    params = {"limit": 10, "window": 60.0}
    policy = create_policy(name, params)
    assert isinstance(policy, RateLimiter)


def test_clear_state():
    policy = FixedWindow(10, 60)
    policy.is_allowed("test", 0)
    policy.clear()
    assert "test" not in policy._starts  # private but test
