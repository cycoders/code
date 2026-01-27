import pytest
from unittest.mock import patch

from formatter_preview.file_utils import get_candidate_files


@patch("subprocess.run")
def test_get_candidate_files(mock_run, capsys) -> None:
    mock_run.return_value = MagicMock(stdout="file.py\nfile.js\n", returncode=0)

    files = get_candidate_files(staged=True)
    assert "file.py" in files

    mock_run.return_value.returncode = 1
    files = get_candidate_files()
    assert not files
    assert "git unavailable" in capsys.readouterr().err
