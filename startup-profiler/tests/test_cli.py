import json
from unittest.mock import Mock, MagicMock, patch
import pytest
from typer.testing import CliRunner
from startup_profiler.cli import app

runner = CliRunner()


def test_analyze_success(mocker):
    mocker.patch("subprocess.run", return_value=MagicMock(returncode=0))
    mock_file = Mock()
    mock_file.read.return_value = json.dumps({"foo": {"total": 0.1}})
    mocker.patch("builtins.open", mock_file)
    mocker.patch("os.unlink")
    result = runner.invoke(app, ["analyze", "test.py"])
    assert result.exit_code == 0


def test_analyze_timeout(mocker):
    mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=[], timeout=30, output=b""))
    result = runner.invoke(app, ["analyze", "test.py"])
    assert result.exit_code == 0
    assert "Timeout" in result.stdout


def test_analyze_error(mocker):
    proc_mock = MagicMock(returncode=1)
    proc_mock.stderr = "error"
    mocker.patch("subprocess.run", return_value=proc_mock)
    result = runner.invoke(app, ["analyze", "test.py"])
    assert result.exit_code == 1
    assert "Runner error" in result.stdout
