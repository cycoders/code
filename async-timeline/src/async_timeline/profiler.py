import asyncio
import threading
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class TaskTracker:
    task: "asyncio.Task"
    coro: "asyncio.Coroutine"
    parent_task: Optional["asyncio.Task"]
    parent_tracker: Optional["TaskTracker"] = None
    children: List["TaskTracker"] = field(default_factory=list)

    created: float = 0.0
    done: Optional[float] = None
    duration: Optional[float] = None
    cancelled: bool = False
    exception: Optional[BaseException] = None

    def __post_init__(self):
        self.created = time.monotonic()

    @property
    def name(self) -> str:
        if hasattr(self.coro, "__qualname__"):
            return self.coro.__qualname__
        return getattr(self.coro, "__name__", "anonymous")

    def on_done(self, profiler: "AsyncProfiler"):
        self.done = time.monotonic()
        self.duration = self.done - self.created
        self.cancelled = self.task.cancelled()
        self.exception = self.task.exception()


class AsyncProfiler:
    def __init__(self, poll_interval: float = 0.01):
        self.poll_interval = poll_interval
        self.tasks: List[TaskTracker] = []
        self.task_to_tracker: Dict[asyncio.Task, TaskTracker] = {}
        self.roots: List[TaskTracker] = []
        self.min_t: float = float("inf")
        self.max_concurrent: int = 0
        self.concurrency_history: List[int] = []
        self._original_create_task = None
        self._stop_event = threading.Event()
        self._sampler_thread: Optional[threading.Thread] = None

    def start(self):
        self._original_create_task = asyncio.create_task
        asyncio.create_task = self._patched_create_task
        self._sampler_thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._sampler_thread.start()

    def stop(self):
        if self._original_create_task:
            asyncio.create_task = self._original_create_task
        self._stop_event.set()
        if self._sampler_thread and self._sampler_thread.is_alive():
            self._sampler_thread.join(timeout=1.0)
        self._build_hierarchy()
        if self.tasks:
            self.min_t = min(t.created for t in self.tasks)
            self.max_t = max((t.done or time.monotonic()) for t in self.tasks)

    def _patched_create_task(self, *args, **kwargs) -> asyncio.Task:
        coro = args[0]
        task = self._original_create_task(*args, **kwargs)
        parent_task = asyncio.current_task()
        tracker = TaskTracker(task, coro, parent_task)
        self.tasks.append(tracker)
        self.task_to_tracker[task] = tracker
        task.add_done_callback(lambda t: tracker.on_done(self))
        return task

    def _sample_loop(self):
        while not self._stop_event.is_set():
            try:
                loop = asyncio.get_running_loop()
                pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
                n = len(pending)
                self.concurrency_history.append(n)
                self.max_concurrent = max(self.max_concurrent, n)
            except RuntimeError:
                pass  # No running loop
            self._stop_event.wait(self.poll_interval)

    def _build_hierarchy(self):
        for tracker in self.tasks:
            if tracker.parent_task and tracker.parent_task in self.task_to_tracker:
                parent = self.task_to_tracker[tracker.parent_task]
                if not parent.children:
                    parent.children = []
                parent.children.append(tracker)
                tracker.parent_tracker = parent
        self.roots = [t for t in self.tasks if t.parent_tracker is None]

    def generate_mermaid(self) -> str:
        lines = [
            "gantt",
            "dateFormat s",
            "title Asyncio Task Timeline",
            "todayMarker off",
        ]

        def esc(name: str) -> str:
            return name.replace(" ", "\\ ").replace(":", "\\:")

        def rec_add(tracker: TaskTracker, lines: list):
            start = max(0.0, tracker.created - self.min_t)
            dur = tracker.duration or (time.monotonic() - tracker.created)
            id_name = tracker.name.replace(" ", "_").replace(".", "_").lower()[:20]
            lines.append(f"{id_name} :{start:.2f}, {dur:.2f}s")
            for child in sorted(tracker.children, key=lambda c: c.created):
                rec_add(child, lines)

        for root in sorted(self.roots, key=lambda r: r.created):
            section_name = esc(root.name)
            lines.append(f"section {section_name}")
            rec_add(root, lines)
        return "```mermaid\n" + "\n".join(lines) + "\n```"