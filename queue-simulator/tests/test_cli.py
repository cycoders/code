import pytest
from queue_simulator.tests.conftest import invoke


class TestCLI:
    def test_help(self, invoke):
        result = invoke("--help")
        assert result.exit_code == 0
        assert "Usage" in result.stdout

    def test_sim_minimal(self, invoke, tmp_path):
        result = invoke("sim", "10", "1")
        assert result.exit_code == 0
        assert "Simulating" in result.stdout
        assert "p95 Latency" in result.stdout

    def test_bad_dist(self, invoke):
        result = invoke("sim", "10", "1", "--dist", "invalid")
        assert result.exit_code != 0
        assert "Unknown dist" in result.stdout

    def test_empirical_no_file(self, invoke):
        result = invoke("sim", "10", "1", "--dist", "empirical")
        assert result.exit_code != 0
        assert "service-file required" in result.stdout

    def test_zero_duration(self, invoke):
        result = invoke("sim", "0", "1")
        assert result.exit_code != 0