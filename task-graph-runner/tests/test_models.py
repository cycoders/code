from task_graph_runner.models import Task, Graph

def test_task_defaults():
    t = Task(name='x', command='echo')
    assert t.deps == [] and t.retries == 0