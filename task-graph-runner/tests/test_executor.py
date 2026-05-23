from task_graph_runner.executor import run_task

def test_run_success():
    assert run_task('echo ok') == 0