import pytest
from git_lfs_migrator.suggester import suggest_globs


@pytest.mark.parametrize(
    "stats, coverage, max_globs, expected",
    [
        (
            {
                ".png": {"total_size": 1000},
                ".zip": {"total_size": 500},
                ".mp4": {"total_size": 200},
            },
            0.8,
            10,
            ["*.png", "*.zip"],
        ),
        (
            {"": {"total_size": 100}},
            1.0,
            1,
            ["*noext-file"],  # Note: simplified, actual uses fallback
        ),
        ({}, 0.95, 10, []),
    ],
)
def test_suggest_globs(stats, coverage, max_globs, expected):
    globs = suggest_globs(stats, coverage, max_globs)
    assert globs == expected
