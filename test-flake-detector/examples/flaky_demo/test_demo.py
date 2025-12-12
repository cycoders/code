import random


def test_stable():
    assert True


def test_flaky():
    # ~30% fail
    assert random.randint(1, 10) >= 8


def test_always_fail():
    assert False