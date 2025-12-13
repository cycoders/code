import pytest
tempfile
from dockerfile_optimizer.renderer import render_mermaid
from dockerfile_optimizer.parser import Instruction


def test_render_mermaid(tmp_path):
    insts = [
        Instruction("FROM", "node", 1, ""),
        Instruction("RUN", "npm install", 2, ""),
    ]
    output = tmp_path / "graph.mmd"
    graph = render_mermaid(insts, str(output))
    assert "graph TD" in graph
    assert "N0[" in graph
    assert "N1[" in graph
    assert "N0 --> N1" in graph
    assert output.read_text() == graph
