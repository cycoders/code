import pytest
from pathlib import Path
from py_call_graph.viz import render_graph, format_mermaid


def test_format_mermaid(tmp_path: Path):
    graph = {'foo': {'bar', 'baz'}}
    md = format_mermaid(graph)
    assert 'foo --> bar' in md
    assert 'graph TD' in md


def test_render_mermaid(tmp_path: Path):
    graph = {'a': {'b'}}
    out = tmp_path / 'g.md'
    render_graph(graph, out)
    assert out.exists()
    assert 'a --> b' in out.read_text()


def test_render_dot(tmp_path: Path):
    graph = {'a': {'b'}}
    out = tmp_path / 'g.dot'
    render_graph(graph, out)
    assert out.exists()
    assert 'digraph' in out.read_text()