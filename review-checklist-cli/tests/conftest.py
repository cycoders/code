import pytest
import subprocess
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_subprocess(monkeypatch):
    """Mock subprocess for all tests."""
    def mock_run(cmd, cwd=None, capture_output=False, text=False, check=False, timeout=None, **kwargs):
        cmd_str = " ".join(cmd)
        if "git rev-parse --git-dir" in cmd_str:
            return MagicMock(returncode=0, stdout=b".git", stderr=b"")
        elif "git diff --name-status" in cmd_str:
            return MagicMock(
                returncode=0,
                stdout="M\tsrc/main.py\nA\tdocker/Dockerfile\nD\ttests/old_test.py\n" ,
                stderr=b"",
            )
        raise ValueError(f"Unexpected git cmd: {cmd_str}")

    monkeypatch.setattr(subprocess, "run", mock_run)