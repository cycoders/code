from h2_priority_analyzer.models import Stream
from h2_priority_analyzer.graph import PriorityGraph


def test_render_tree(capsys):
    # Mock console
    from h2_priority_analyzer.visualizer import render_tree, console
    streams = [Stream(id=1)]
    graph = PriorityGraph(streams)
    render_tree(streams, graph)
    captured = capsys.readouterr()
    assert "Tree" in captured.out

# Viz tests are visual, focus on logic above
