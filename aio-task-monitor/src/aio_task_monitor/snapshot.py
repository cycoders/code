import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class TaskInfo:
    task_id: int
    name: str
    coro_name: str
    done: bool
    cancelled: bool
    stack: List[str]


def take_snapshot() -> Dict[str, Any]:
    """
    Take a safe snapshot of the current event loop's tasks.

    Returns:
        Dict with 'stats' and 'tasks' lists.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return {
            "error": "No running event loop found",
            "stats": {"num_tasks": 0, "num_running": 0, "num_done": 0, "num_cancelled": 0, "loop_running": False},
            "tasks": [],
        }

    tasks = list(asyncio.all_tasks(loop))
    task_infos: List[TaskInfo] = []

    for task in tasks:
        coro = task.get_coro()
        coro_name = coro.__qualname__ if coro else "<unknown>"
        try:
            stack = task.print_stack()[-10:]  # Last 10 frames
        except Exception:
            stack = []
        task_infos.append(
            TaskInfo(
                task_id=id(task),
                name=task.get_name() or "unnamed",
                coro_name=coro_name,
                done=task.done(),
                cancelled=task.cancelled(),
                stack=[str(frame) for frame in stack],
            )
        )

    stats = {
        "num_tasks": len(tasks),
        "num_running": len([t for t in task_infos if not t.done]),
        "num_done": len([t for t in task_infos if t.done and not t.cancelled]),
        "num_cancelled": len([t for t in task_infos if t.cancelled]),
        "loop_running": loop.is_running(),
    }

    return {
        "stats": stats,
        "tasks": [asdict(ti) for ti in task_infos],
    }