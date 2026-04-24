import pytest
from password_strength_simulator.hardware import (
    get_log10_speed,
    list_hardware,
    list_algos,
    ALGO_COST_TYPE,
)


@pytest.mark.parametrize(
    "algo, cost, hardware, exp_approx",
    [
        ("md5", 0, "cpu-i9", 10.18),
        ("bcrypt", 12, "rtx4090", 5.33),
        ("bcrypt", 13, "rtx4090", 5.33 - math.log10(2)),  # pow2
        ("pbkdf2-sha256", 200000, "cpu-i9", 8.0 - math.log10(2)),  # iter
    ],
)
def test_get_log10_speed(algo: str, cost: int, hardware: str, exp_approx: float):
    result = get_log10_speed(algo, cost, hardware)
    assert abs(result - exp_approx) < 0.1


@pytest.mark.parametrize("what", ["invalid-algo", "invalid-hw"])
def test_get_log10_speed_errors(what: str):
    with pytest.raises(ValueError):
        if what == "invalid-algo":
            get_log10_speed("foo", 12, "cpu-i9")
        else:
            get_log10_speed("md5", 0, "foo")


def test_lists():
    assert "rtx4090" in list_hardware()
    assert "bcrypt" in list_algos()