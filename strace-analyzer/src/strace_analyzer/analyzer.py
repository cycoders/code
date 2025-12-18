import json
import logging
from collections import defaultdict, Counter
from typing import Any, Dict, List, Literal

from .models import StraceEvent

logger = logging.getLogger(__name__)

IO_SYSCALLS = {
    "read",
    "readv",
    "pread64",
    "write",
    "writev",
    "pwrite64",
    "openat",
    "open",
    "close",
}
NET_SYSCALLS = {"connect", "bind", "sendto", "recvfrom", "socket"}


def analyze(events: List[StraceEvent], group_by: str = "all") -> Dict[str, Any]:
    """Analyze events into stats dict."""
    syscall_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})
    bytes_read = 0
    bytes_written = 0
    file_opens = Counter()

    for event in events:
        stats = syscall_stats[event.syscall]
        stats["count"] += 1
        if event.duration:
            stats["total_time"] += event.duration

        # Bytes from read/write
        if event.syscall in {"read", "readv", "pread64"} and event.result.isdigit():
            bytes_read += int(event.result)
        elif event.syscall in {"write", "writev", "pwrite64"} and event.result.isdigit():
            bytes_written += int(event.result)

        # File opens
        if event.syscall == "openat" and len(event.args) >= 2 and event.args[0] == "AT_FDCWD":
            path = event.args[1].strip('"\'')
            file_opens[path] += 1

    # Compute avgs, totals
    total_time = sum(s["total_time"] for s in syscall_stats.values())
    total_events = sum(s["count"] for s in syscall_stats.values())

    top_syscalls = sorted(
        syscall_stats.items(), key=lambda x: x[1]["total_time"], reverse=True
    )[:15]

    # Grouped
    groups = _group_stats(syscall_stats, events)

    stats = {
        "total_events": total_events,
        "total_time": total_time,
        "avg_time": total_time / total_events if total_events else 0,
        "bytes_read": bytes_read,
        "bytes_written": bytes_written,
        "top_file_opens": file_opens.most_common(10),
        "top_syscalls": [
            {
                **item[1],
                "syscall": item[0],
                "avg_time": item[1]["total_time"] / item[1]["count"],
                "pct_time": (item[1]["total_time"] / total_time * 100) if total_time else 0,
            }
            for item in top_syscalls
        ],
        "groups": groups,
    }
    return stats


def _group_stats(syscall_stats: Dict, events: List[StraceEvent]) -> Dict[str, Dict]:
    groups = defaultdict(lambda: {"count": 0, "total_time": 0.0})
    for syscall, stats in syscall_stats.items():
        if any(s in syscall for s in IO_SYSCALLS):
            g = groups["IO"]
        elif any(s in syscall for s in NET_SYSCALLS):
            g = groups["Network"]
        else:
            g = groups["Other"]
        g["count"] += stats["count"]
        g["total_time"] += stats["total_time"]
    return dict(groups)
