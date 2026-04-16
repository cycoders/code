import pytest
from pathlib import Path
from datetime import datetime

from shell_history_analyzer.parser import parse_zsh_line, parse_bash_lines, detect_format, parse_history_file


@pytest.mark.parametrize(
    "line,expected_cmd",
    [
        (": 1699000000:0;git status", "git"),
        (": 1699000001:0;ls -la 'file name'", "ls"),
    ],
)
def test_parse_zsh_line(line, expected_cmd):
    entry = parse_zsh_line(line)
    assert entry is not None
    assert entry.command == expected_cmd
    assert len(entry.words) >= 1


def test_parse_zsh_invalid():
    assert parse_zsh_line("invalid") is None


def test_parse_bash_lines(sample_bash_file):
    lines = sample_bash_file.read_text().splitlines()
    entries = parse_bash_lines(lines)
    assert len(entries) == 2
    assert entries[0].command == "ls"
    assert entries[1].command == "git"


def test_detect_format(tmp_path: Path):
    zsh_file = tmp_path / "zsh"
    zsh_file.write_text(": 123:0;git")
    assert detect_format(zsh_file) == "zsh"

    bash_file = tmp_path / "bash"
    bash_file.write_text("#123\nls")
    assert detect_format(bash_file) == "bash"


def test_parse_history_file(sample_bash_file):
    entries = parse_history_file(sample_bash_file, "bash")
    assert len(entries) == 2
