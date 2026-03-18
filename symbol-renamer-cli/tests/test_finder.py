import pytest
from pathlib import Path

from symbol_renamer_cli.finder import get_py_files, should_process


class TestFinder:
    @pytest.fixture
    def tmp_structure(self, tmp_path: Path) -> Path:
        tmp_path.joinpath("src").mkdir()
        tmp_path.joinpath("src/main.py").touch()
        tmp_path.joinpath("venv").mkdir()
        tmp_path.joinpath("venv/script.py").touch()
        tmp_path.joinpath(".git/ignore.py").touch()
        return tmp_path

    def test_get_py_files(self, tmp_structure: Path, mocker: pytest.MonkeyPatch) -> None:
        mock_console = mocker.Mock()
        files = get_py_files([tmp_structure], mock_console)
        assert len(files) == 1  # only src/main.py
        assert files[0].name == "main.py"

    def test_should_process(self) -> None:
        p1 = Path("/project/src/main.py")
        assert should_process(p1, set()) is True

        p2 = Path("/project/venv/script.py")
        assert should_process(p2, {"venv"}) is False

        p3 = Path("/project/.hidden/main.py")
        assert should_process(p3, set()) is False