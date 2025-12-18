import pytest
from pathlib import Path

from strace_analyzer.parser import parse_strace, _parse_line
from strace_analyzer.models import StraceEvent


@pytest.fixture
def sample_lines():
    return [
        '1234 0.000123 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3 <0.000045>',
        '1234 0.000234 read(3, "\\177ELF\\2\\1\\1\\0\\0\\0", 64) = 64 <0.000012>',
        '1234 0.001234 futex(0x7f, FUTEX_WAIT, 0, NULL) = ? ERESTARTSYS (To be restarted if SA_RESTART is set)',
        '5678 2.345678 +++ exited with 0 +++',
        '1234 0.002345 close(3) = 0 <0.000001>',
        'invalid line',
    ]


def test_parse_line_open(sample_lines):
    line = sample_lines[0]
    event = _parse_line(line)
    assert event is not None
    assert event.pid == 1234
    assert event.syscall == "openat"
    assert event.args[0] == "AT_FDCWD"
    assert event.args[1] == '"/etc/ld.so.cache"'
    assert event.result == "3"
    assert event.duration == 0.000045


def test_parse_line_read(sample_lines):
    line = sample_lines[1]
    event = _parse_line(line)
    assert event.duration == 0.000012
    assert "read" in event.syscall


def test_parse_line_futex_restart(sample_lines):
    line = sample_lines[2]
    event = _parse_line(line)
    assert event.notes == "? ERESTARTSYS (To be restarted if SA_RESTART is set)"


def test_parse_exit(sample_lines):
    line = sample_lines[3]
    event = _parse_line(line)
    assert event.syscall == "exit"
    assert event.result == "0"


def test_parse_invalid(sample_lines):
    line = sample_lines[5]
    event = _parse_line(line)
    assert event is None


def test_parse_file(tmp_path: Path):
    sample_file = tmp_path / "trace.log"
    with sample_file.open("w") as f:
        for line in [l for l in ['1234 0.001 open() = 0']]:
            f.write(line + "\n")

    events = parse_strace(sample_file)
    assert len(events) == 1
