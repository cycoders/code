import pytest
from test_suite_splitter.models import TestCase
from test_suite_splitter.splitter import split_tests, Job


class TestSplitter:
    @pytest.fixture
    def sample_tests(self) -> list[TestCase]:
        return [
            TestCase("slow", "slow1", 2.5),
            TestCase("slow", "slow2", 1.8),
            TestCase("slow", "slow3", 0.7),
            TestCase("fast", "fast1", 0.6),
            TestCase("fast", "fast2", 0.523),
        ]

    def test_split_basic(self, sample_tests: list[TestCase]) -> None:
        jobs = split_tests(sample_tests, 2)
        assert len(jobs) == 2
        totals = [j.total_duration for j in jobs]
        assert max(totals) - min(totals) <= 0.1  # balanced
        assert sum(totals) == 6.123

    def test_split_one_job(self, sample_tests: list[TestCase]) -> None:
        jobs = split_tests(sample_tests, 1)
        assert len(jobs) == 1
        assert jobs[0].count == 5
        assert jobs[0].total_duration == 6.123

    def test_split_empty(self) -> None:
        jobs = split_tests([], 3)
        assert len(jobs) == 3
        assert all(j.count == 0 for j in jobs)

    def test_split_large_imbalance(self) -> None:
        # Extreme: one very slow test
        tests = [TestCase("a", "slow", 100)] + [TestCase("b", f"fast{i}", 0.1) for i in range(20)]
        jobs = split_tests(tests, 3)
        slow_job = max(jobs, key=lambda j: j.total_duration)
        assert slow_job.tests[0].duration == 100
        assert max(j.total_duration for j in jobs) <= 100.5

    def test_jobs_add_correctly(self) -> None:
        job = Job(0)
        t1 = TestCase("a", "t1", 1.0)
        job.add(t1)
        assert job.tests == [t1]
        assert job.total_duration == 1.0
        assert job.count == 1