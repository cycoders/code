import pytest
from test_suite_splitter.models import TestCase
from test_suite_splitter.output import output_json
from test_suite_splitter.splitter import Job


class TestOutput:
    def test_json_structure(self) -> None:
        jobs = [Job(0)]
        jobs[0].tests = [TestCase("a", "t1", 1.0)]
        jobs[0].total_duration = 1.0
        jobs[0].count = 1
        json_str = output_json(jobs, 1, 1.0)
        data = json.loads(json_str)
        assert data["meta"]["total_tests"] == 1
        assert data["jobs"][0]["test_count"] == 1

    @pytest.mark.parametrize("balance", [1.0, 1.05, 2.0])
    def test_balance_calc(self, balance: float) -> None:
        # Implicit via splitter tests