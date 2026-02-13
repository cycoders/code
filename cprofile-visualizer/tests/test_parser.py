import pytest
from pathlib import Path
from cprofile_visualizer.parser import load_profile, get_sort_key
from cprofile_visualizer import parser


def test_load_profile(sample_prof: Path):
    stats = load_profile(sample_prof)
    assert len(stats.stats) > 10
    assert len(stats.fcn_list) > 0
    assert "slow_func" in str(stats.fcn_list[0])


@pytest.mark.parametrize("cli_sort,pstats_sort", [
    ("cumtime", "cumulative"),
    ("tottime", "time"),
    ("calls", "calls"),
    ("filename", "filename"),
    ("invalid", "invalid"),
])
def test_get_sort_key(cli_sort: str, pstats_sort: str):
    assert get_sort_key(cli_sort) == pstats_sort


def test_load_profile_errors(tmp_path: Path):
    bad_path = tmp_path / "nonexistent.prof"
    with pytest.raises(FileNotFoundError):
        load_profile(bad_path)

    empty_path = tmp_path / "empty.prof"
    empty_path.touch()
    with pytest.raises(ValueError, match="Empty profile"):
        load_profile(empty_path)
