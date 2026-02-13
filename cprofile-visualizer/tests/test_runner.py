import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from cprofile_visualizer.runner import profile_run


@patch("subprocess.run")
def test_profile_run_success(mock_run: MagicMock, tmp_path: Path):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stderr = ""

    output = tmp_path / "out.prof"
    profile_run("test.py", output, ["arg1"])

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[0:5] == ["python", "-m", "cProfile", "-o", str(output)]
    assert cmd[5] == "test.py"
    assert cmd[6:] == ["arg1"]


@patch("subprocess.run")
def test_profile_run_failure(mock_run: MagicMock):
    mock_run.return_code = 1
    mock_run.stderr = "Error"

    with pytest.raises(SystemExit):
        profile_run("fail.py", Path("out.prof"), [])
