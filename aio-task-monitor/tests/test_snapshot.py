import asyncio
import pytest
from unittest.mock import Mock, patch
from aio_task_monitor.snapshot import take_snapshot, TaskInfo


@pytest.fixture
async def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def test_take_snapshot_no_loop():
    with patch("asyncio.get_running_loop", side_effect=RuntimeError("no loop")):
        data = take_snapshot()
        assert data["error"] == "No running event loop found"
        assert data["stats"]["num_tasks"] == 0


def test_take_snapshot_mock_tasks():
    mock_loop = Mock()
    mock_task1 = Mock()
    mock_task1.get_name.return_value = "test1"
    mock_task1.done.return_value = False
    mock_task1.cancelled.return_value = False
    mock_task1.get_coro.return_value = Mock(__qualname__="TestCoro")
    mock_task1.print_stack.return_value = ["frame1", "frame2"]

    mock_task2 = Mock()
    mock_task2.get_name.return_value = None
    mock_task2.done.return_value = True
    mock_task2.cancelled.return_value = True

    mock_loop.all_tasks.return_value = {mock_task1, mock_task2}
    mock_loop.is_running.return_value = True

    with patch("asyncio.get_running_loop", return_value=mock_loop):
        data = take_snapshot()
        assert len(data["tasks"]) == 2
        assert data["tasks"][0]["name"] == "test1"
        assert data["tasks"][0]["coro_name"] == "TestCoro"
        assert data["stats"]["num_tasks"] == 2
        assert data["stats"]["num_running"] == 1
