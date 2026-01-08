import asyncio
import time
from unittest.mock import Mock, patch, MagicMock

import pytest

from async_timeline.profiler import AsyncProfiler, TaskTracker


@pytest.fixture
def mock_coro():
    coro = Mock()
    coro.__qualname__ = "test_coro"
    return coro


@pytest.fixture
def mock_task():
    task = Mock(spec=asyncio.Task)
    task.cancelled.return_value = False
    task.exception.return_value = None
    task.done.return_value = False
    return task


class TestTaskTracker:
    def test_on_done(self, mock_task, mock_coro):
        tracker = TaskTracker(mock_task, mock_coro, None)
        before = time.monotonic()
        tracker.on_done(mock_task)
        after = time.monotonic()
        assert tracker.done is not None
        assert before <= tracker.done <= after
        assert tracker.duration is not None
        assert tracker.duration > 0
        assert not tracker.cancelled

    @patch.object(TaskTracker, "on_done")
    def test_on_done_called(self, mock_on_done, mock_task, mock_coro):
        tracker = TaskTracker(mock_task, mock_coro, None)
        mock_task.add_done_callback = Mock()
        # Simulate add_done_callback
        tracker.on_done(mock_task)
        mock_on_done.assert_called_once_with(mock_task)


class TestAsyncProfiler:
    def test_patch_create_task(self, mock_coro, mock_task):
        profiler = AsyncProfiler()
        orig_create = Mock(return_value=mock_task)
        profiler._original_create_task = orig_create

        loop = Mock()
        patched_task = profiler._patched_create_task(loop, mock_coro)

        orig_create.assert_called_once_with(loop, mock_coro)
        assert patched_task == mock_task
        assert len(profiler.tasks) == 1
        tracker = profiler.tasks[0]
        assert tracker.name == "test_coro"
        assert mock_task in profiler.task_to_tracker

    def test_sample_loop_no_loop(self):
        profiler = AsyncProfiler(0.001)
        # RuntimeError if no loop
        profiler._stop_event.set()
        profiler._sample_loop()  # Should not crash

    def test_build_hierarchy(self):
        profiler = AsyncProfiler()
        parent_task = Mock()
        child_task = Mock()
        parent_tracker = TaskTracker(parent_task, Mock(), None)
        child_tracker = TaskTracker(child_task, Mock(), parent_task)
        profiler.tasks = [parent_tracker, child_tracker]
        profiler.task_to_tracker = {parent_task: parent_tracker, child_task: child_tracker}

        profiler._build_hierarchy()

        assert len(parent_tracker.children) == 1
        assert child_tracker.parent_tracker == parent_tracker
        assert profiler.roots == [parent_tracker]

    def test_roots_no_parent(self):
        profiler = AsyncProfiler()
        tracker1 = TaskTracker(Mock(), Mock(), None)
        tracker2 = TaskTracker(Mock(), Mock(), None)
        profiler.tasks = [tracker1, tracker2]
        profiler._build_hierarchy()
        assert set(profiler.roots) == {tracker1, tracker2}
