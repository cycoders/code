import os
import subprocess
from pathlib import Path

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_git_log(mocker: MockerFixture):
    """Mock subprocess for git log."""
    return mocker.patch("subprocess.check_output")


@pytest.fixture
def sample_git_output() -> str:
    return """a1b2c3d4e5f6789012345678901234567890ab
1640995200\tauthor1\tInitial commit
file1.py\t10\t2
file2.py\t0\t5

f1e2d3c4b5a6978012345678901234567890abcf
1641081600\tauthor2\tFix bug
file1.py\t3\t1
file3.txt\t20\t0
"""
