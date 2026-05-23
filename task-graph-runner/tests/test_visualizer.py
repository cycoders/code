from task_graph_runner.models import Graph, Task
from task_graph_runner.visualizer import to_mermaid

def test_mermaid_output():
    g = Graph(tasks={'a': Task('a', 'echo')})
    assert 'graph TD' in to_mermaid(g)