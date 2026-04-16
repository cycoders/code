import pytest
from pathlib import Path

from shell_history_analyzer.types import HistoryEntry


@pytest.fixture
def sample_zsh_entries():
    return [
        HistoryEntry(
            timestamp=None,
            command="git",
            full_line=": 1699000000:0;git status",
            words=["git", "status"],
        ),
        HistoryEntry(
            timestamp=None,
            command="ls",
            full_line=": 1699000001:0;ls -la",
            words=["ls", "-la"],
        ),
    ]


@pytest.fixture
def sample_bash_file(tmp_path: Path):
    p = tmp_path / "history.bash"
    p.write_text("#1700000000\nls -la\n#1700000001\ngit status\n")
    return p
