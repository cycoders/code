import pytest
from ratelimit_simulator.utils import resample, render_sparkline


@pytest.mark.parametrize(
    "values, bins, expected_len",
    [([], 10, 10), ([1], 10, 1), ([1, 2, 3], 2, 2)],
)
def test_resample(values, bins, expected_len):
    res = resample(values, bins)
    assert len(res) == bins
    assert all(0 <= v <= max(values + [0]) for v in res)


@pytest.mark.parametrize(
    "values, width",
    [([0, 1, 0, 1], 10), ([1] * 5, 20), ([0] * 3, 5)],
)
def test_render_sparkline(values, width):
    line = render_sparkline(values, width)
    assert len(line) == width
    assert all(c in " ▁▂▃▄▅▆▇█" for c in line)
