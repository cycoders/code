import pytest
from sql_explain_viz.models import PlanNode
from sql_explain_viz.renderer import render_ascii, render_mermaid


def test_render_ascii():
    node = PlanNode("Root", children=[PlanNode("Child")])
    ascii_art = render_ascii(node)
    assert "Root" in ascii_art
    assert "Child" in ascii_art
    assert "└── " in ascii_art or "├── " in ascii_art


def test_render_mermaid():
    node = PlanNode("Root", children=[PlanNode("Child")])
    mermaid = render_mermaid(node)
    assert "flowchart TD" in mermaid
    assert "Root" in mermaid
    assert "Child" in mermaid
    assert "-->" in mermaid