import math
import pytest
from password_strength_simulator.simulator import (
    compute_log10_attempts,
    CrackResult,
    analyze_password,
    CHARSET_SIZES,
)


@pytest.mark.parametrize(
    "charset_size, length, expected",
    [
        (95, 12, 12 * math.log10(95)),
        (62, 8, 8 * math.log10(62)),
        (26, 1, math.log10(26)),
    ],
)
def test_compute_log10_attempts(charset_size: int, length: int, expected: float):
    result = compute_log10_attempts(charset_size, length)
    assert math.isclose(result, expected, rel_tol=1e-9)


@pytest.mark.parametrize(
    "pw, expected_size",
    [
        ("abc", 95),
        ("Ab1!", 95),
        ("123", 95),
    ],
)
def test_analyze_password(pw: str, expected_size: int):
    length, size = analyze_password(pw, expected_size)
    assert length == len(pw)
    assert size == expected_size


def test_crack_result_format():
    # Mock console
    res_short = CrackResult(3.0, 3.0)  # 1s
    assert "s" in res_short.format_time(None)[0]

    res_long = CrackResult(40.0, 10.0)  # 10^30 s ~ insane years
    assert "years" in res_long.format_time(None)[0]