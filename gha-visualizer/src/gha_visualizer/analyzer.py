from collections import defaultdict, Counter
from typing import List, Dict, Any

from .models import Job


def analyze(jobs: List[Job]) -> Dict[str, Any]:
    """Compute analytics and detect issues for workflow jobs."""

    num_jobs = len(jobs)
    total_steps = sum(len(job.steps) for job in jobs)

    # Dependency stats
    indegrees = Counter()
    max_outdegree = 0
    for job in jobs:
        outdegree = len(job.needs)
        max_outdegree = max(max_outdegree, outdegree)
        for need in job.needs:
            indegrees[need] += 1
    max_indegree = max(indegrees.values(), default=0)

    # Issues
    issues = []
    for job in jobs:
        if job.name in job.needs:
            issues.append(f"Self-dependency detected in '{job.name}' job")
        if len(job.steps) > 25:
            issues.append(f"Long job '{job.name}' has {len(job.steps)} steps (consider splitting)")
        if job.strategy and len(job.steps) > 15:
            issues.append(f"Matrix job '{job.name}' may explode with {len(job.steps)} steps")

    # Estimated parallelism (rough: max simultaneous jobs ~ 1 + avg indegree)
    avg_indegree = sum(indegrees.values()) / num_jobs if num_jobs else 0
    parallelism_estimate = int(1 + avg_indegree)

    return {
        'jobs': num_jobs,
        'steps': total_steps,
        'max_outdegree': max_outdegree,
        'max_indegree': max_indegree,
        'parallelism_estimate': parallelism_estimate,
        'issues': issues,
    }