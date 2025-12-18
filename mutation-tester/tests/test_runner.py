import pytest
import subprocess
from unittest.mock import MagicMock
from pathlib import Path
from mutation_tester.runner import find_pyfiles, run_mutations, run_pytest, Config


class TestUtils:
    def test_find_pyfiles(self, sample_project: Path):
        cfg = Config(sample_project, [], [], [], 0, 0, 0.0, False)
        files = list(find_pyfiles(sample_project, cfg.exclude_patterns))
        assert len(files) == 2  # foo.py, bar.py

    def test_run_pytest_timeout(self, tmp_path: Path):
        cfg = Config(tmp_path, [], [], [], 0.1, 0, 0.0, False)
        with pytest.raises(subprocess.TimeoutExpired):
            run_pytest(tmp_path, cfg)


class TestRunMutations:
    @pytest.fixture
    def mock_pytest(self, monkeypatch):
        def mock_run(cmd, **kwargs):
            class Result:
                returncode = 1  # killed
            return Result()
        monkeypatch.setattr(subprocess, "run", mock_run)

    def test_integration(self, sample_project: Path, mock_pytest, monkeypatch):
        monkeypatch.setenv("PATH", "/usr/bin")  # avoid pytest not found
        cfg = Config(sample_project, [], ["-q"], 10, 10, 80.0, False)
        results = run_mutations(sample_project, cfg, False)
        assert results["total_mutants"] > 0
        assert results["overall_score"] > 0