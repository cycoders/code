from flamegraph_diff_cli.render import render_terminal, render_html
from types import SimpleNamespace

def test_render_html():
    res = SimpleNamespace(regressions=[], improvements=[], total_delta=0)
    assert 'Diff ready' in render_html(res)