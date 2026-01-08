import pytest
from unittest.mock import Mock

from async_timeline.profiler import AsyncProfiler
from async_timeline.reporter import generate_report, _concurrency_heatmap


def test_concurrency_heatmap_empty():
    heatmap = _concurrency_heatmap([], 0)
    assert "No concurrency data" in heatmap


def test_concurrency_heatmap_simple():
    history = [1, 2, 1, 3, 2]
    heatmap = _concurrency_heatmap(history, 3)
    assert "█" in heatmap
    assert "░" in heatmap
    assert "─" in heatmap


@pytest.mark.parametrize("n_tasks", [0, 5])
def test_generate_report_no_crash(n_tasks, capsys):
    profiler = Mock(spec=AsyncProfiler)
    profiler.tasks = [Mock(duration=1.0) for _ in range(n_tasks)]
    profiler.max_concurrent = 3
    profiler.concurrency_history = [1, 2, 3]
    profiler.generate_mermaid.return_value = "mock mermaid"
    profiler.roots = []

    generate_report(profiler, Mock())
    captured = capsys.readouterr()
    assert "Summary" in captured.out
    if n_tasks:
        assert "Slowest Tasks" in captured.out
