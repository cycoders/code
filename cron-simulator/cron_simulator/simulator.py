from typing import List
from datetime import datetime, timedelta

from croniter import croniter
from zoneinfo import ZoneInfo

from cron_simulator.models import Job, Execution


def simulate_jobs(jobs: List[Job], start: datetime, end: datetime) -> List[Execution]:
    """Simulate all job executions in [start, end]."""
    executions: List[Execution] = []
    tz = ZoneInfo(start.tzinfo.zone) if start.tzinfo else ZoneInfo("UTC")

    for job in jobs:
        iter_start = start.astimezone(tz)
        it = croniter(job.cron, iter_start)
        while True:
            try:
                run_start = it.get_next(datetime)
            except StopIteration:
                break
            if run_start > end:
                break
            run_end = run_start + timedelta(seconds=job.duration)
            executions.append(Execution(job.name, run_start, run_end))

    return sorted(executions, key=lambda e: e.start)


def detect_overlaps(executions: List[Execution]) -> List[tuple[datetime, List[str]]]:
    """Detect overlapping executions using sweep line."""
    if not executions:
        return []

    events = []
    for e in executions:
        events.append((e.start, "start", e.job_name))
        events.append((e.end, "end", e.job_name))

    events.sort(key=lambda x: (x[0], x[1] != "start"))  # Ends before starts at same time

    active_jobs: set[str] = set()
    overlaps: List[tuple[datetime, List[str]]] = []

    for timestamp, event_type, job_name in events:
        if event_type == "start":
            if active_jobs:
                overlaps.append((timestamp, sorted(list(active_jobs) + [job_name])))
            active_jobs.add(job_name)
        else:
            active_jobs.discard(job_name)

    return overlaps