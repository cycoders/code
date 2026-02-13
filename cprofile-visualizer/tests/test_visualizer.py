import pytest
from unittest.mock import Mock
from cprofile_visualizer.visualizer import render_table, render_tree, render_flame


@pytest.mark.parametrize("renderer", [render_table, render_tree, render_flame])
def test_renderers_no_crash(sample_prof, renderer: str, capsys):
    from cprofile_visualizer.parser import load_profile

    stats = load_profile(sample_prof)
    console = Mock()
    renderer(stats, limit=5, console=console)
    captured = capsys.readouterr()
    assert not captured.err  # No errors


def test_flame_total_time(sample_prof):
    from cprofile_visualizer.parser import load_profile
    from cprofile_visualizer.visualizer import render_flame

    stats = load_profile(sample_prof)
    # Top cumtime should be ~total
    top_ct = stats.stats[stats.fcn_list[0]][3]
    assert top_ct > 0.001  # Meaningful
