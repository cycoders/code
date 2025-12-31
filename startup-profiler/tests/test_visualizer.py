import pytest
from startup_profiler.visualizer import render_flamegraph_svg, render_table, render_html_report


@pytest.fixture
def sample_timings():
    return {
        "numpy": {"total": 0.15, "self": 0.12, "size": 8000},
        "pandas": {"total": 0.25, "self": 0.05, "size": 120},
        "_meta": {"total_time": 0.40},
    }


def test_render_flamegraph_svg(sample_timings):
    svg = render_flamegraph_svg(sample_timings)
    assert '<svg' in svg
    assert '<rect' in svg
    assert '</svg>' in svg
    assert len(svg) > 1000


def test_render_table(capsys, sample_timings):
    console = Mock()
    render_table(sample_timings, console)
    captured = capsys.readouterr()
    assert "Table" in captured.out


def test_render_html_report(sample_timings):
    html = render_html_report(sample_timings)
    assert "<html>" in html
    assert "<svg" in html
    assert "numpy" in html
    assert "pandas" in html
