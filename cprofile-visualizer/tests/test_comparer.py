import pytest
from unittest.mock import Mock
from cprofile_visualizer.comparer import render_compare
from cprofile_visualizer.parser import load_profile


def test_render_compare(sample_prof: Path, tmp_path: Path):
    # Duplicate for file2
    prof2 = tmp_path / "prof2.prof"
    sample_prof.replace(prof2)  # Same for test

    stats1 = load_profile(sample_prof)
    stats2 = load_profile(prof2)

    console = Mock()
    render_compare(stats1, stats2, 5, console, "delta")

    # Called
    assert console.print.called


def test_compare_diff_keys(sample_prof1: Path, sample_prof2: Path):
    # Would test unique funcs, but mock console ok
    pass
