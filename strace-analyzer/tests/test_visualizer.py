import io
from unittest.mock import patch

import pytest
from rich.console import Console

from strace_analyzer.visualizer import format_bytes, print_summary


@pytest.mark.parametrize(
    "n,expected",
    [(0, "0.0 B"), (1024, "1.0 KB"), (1024**2, "1.0 MB"), (1024**3, "1.0 GB")],
)
def test_format_bytes(n, expected):
    assert format_bytes(n) == expected


def test_print_summary(capsys):
    stats = {
        "top_syscalls": [{"syscall": "test", "count": 1, "total_time": 1.0, "avg_time": 1.0, "pct_time": 100.0}],
        "bytes_read": 1024,
        "bytes_written": 512,
        "top_file_opens": [("/test", 1)],
        "groups": {"IO": {"count": 1, "total_time": 1.0}},
    }
    console = Console(file=io.StringIO())
    with patch("strace_analyzer.visualizer.console", console):
        print_summary(stats)
    captured = capsys.readouterr()
    assert "Top Syscalls" in captured.out
