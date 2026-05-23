import tempfile
from pathlib import Path
import pytest
from task_graph_runner.parser import load_graph

def test_load_simple_graph():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write('tasks:\n- name: build\n  command: echo build')
        f.flush()
        g = load_graph(Path(f.name))
        assert 'build' in g.tasks