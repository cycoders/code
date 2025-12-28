from typing import List

from .models import TestCase


class Job:
    """A single CI job shard with tests and aggregate metrics."""

    def __init__(self, index: int):
        self.index = index
        self.tests: list[TestCase] = []
        self.total_duration = 0.0
        self.count = 0

    def add(self, test: TestCase) -> None:
        self.tests.append(test)
        self.total_duration += test.duration
        self.count += 1


def split_tests(tests: list[TestCase], num_jobs: int) -> list[Job]:
    """
    Split tests into balanced jobs using First-Fit Decreasing (FFD) bin packing.

    - Sort tests descending by duration
    - Assign each to the current least-loaded job

    Time: O(n log n + n * k), k=num_jobs
    Approx-optimal for large n.
    """
    if num_jobs < 1:
        raise ValueError("num_jobs must be >= 1")
    if not tests:
        return [Job(i) for i in range(num_jobs)]

    sorted_tests = sorted(tests, key=lambda t: t.duration, reverse=True)
    jobs = [Job(i) for i in range(num_jobs)]

    for test in sorted_tests:
        # Find job with minimal load
        least_loaded = min(jobs, key=lambda j: j.total_duration)
        least_loaded.add(test)

    return jobs