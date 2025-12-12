import pytest
from unittest.mock import MagicMock

from test_flake_detector.runner import run_experiments


def test_run_experiments_cmd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mock_run = MagicMock()
    monkeypatch.setattr("subprocess.run", mock_run)

    progress_mock = MagicMock()
    task_mock = MagicMock()
    progress_mock.add_task.return_value = 0
    progress_mock.advance = lambda x: None

    run_experiments(1, ["tests/"], tmp_path, progress_mock, 0)

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[:3] == ["pytest", "-v", "--tb=no"]
    assert "tests/" in cmd