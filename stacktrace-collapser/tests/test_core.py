import pytest
from stacktrace_collapser.core import collapse_frames
from stacktrace_collapser.models import Frame


@pytest.mark.parametrize("frames, threshold, expected_counts", [
    ([], 2, []),
    ([Frame(file="a.py", line=1, func="f")], 2, [1]),
    (
        [Frame(file="v.py", line=42, func="h")] * 5,
        2,
        [5],
    ),
    (
        [
            Frame(file="v.py", line=42, func="h"),
            Frame(file="a.py", line=10, func="m"),
            Frame(file="v.py", line=42, func="h"),
        ],
        2,
        [1, 1, 1],
    ),  # non-consecutive
    (
        [Frame(file="v.py", line=42, func="h")] * 1 + [Frame(file="a.py", line=10, func="m")],
        3,
        [1, 1],
    ),  # below threshold
])
def test_collapse_frames(frames, threshold, expected_counts):
    collapsed = collapse_frames(frames, threshold)
    assert len(collapsed) == len(expected_counts)
    counts = [f.count for f in collapsed]
    assert counts == expected_counts
