import pytest
import subprocess
from pathlib import Path


 def test_version(script_runner):
    ret = script_runner.run("python", "-m", "loadtest_analyzer.cli", "version")
    assert ret.success
    assert "0.1.0" in ret.stdout

# Note: Full CLI tests require typer-cli or subprocess mocking, kept light

@pytest.fixture
 def script_runner():
    def _run(*args):
        return subprocess.run(["python", "-m", "loadtest_analyzer.cli", *args], capture_output=True, text=True)
    return _run
