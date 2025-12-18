import pytest
from collections import Counter

from strace_analyzer.models import StraceEvent
from strace_analyzer.analyzer import analyze, IO_SYSCALLS


@pytest.fixture
def sample_events():
    return [
        StraceEvent(0.0, 1234, "openat", ["AT_FDCWD", "/file"], "3", 0.001, None),
        StraceEvent(0.1, 1234, "read", ["3"], "1024", 0.0005, None),
        StraceEvent(0.2, 1234, "futex", [], "-1", 0.01, None),
        StraceEvent(0.3, 5678, "write", ["4"], "512", 0.0002, None),
    ]


def test_analyze_basic(sample_events):
    stats = analyze(sample_events)
    assert stats["total_events"] == 4
    assert stats["bytes_read"] == 1024
    assert stats["bytes_written"] == 512
    assert len(stats["top_syscalls"]) == 4
    assert stats["top_file_opens"][0][0] == "/file"


def test_analyze_zero_duration(sample_events):
    e = sample_events[0]
    e.duration = None
    stats = analyze(sample_events)
    assert stats["total_time"] > 0  # others have duration


def test_groups(sample_events):
    stats = analyze(sample_events)
    groups = stats["groups"]
    assert groups["IO"]["count"] >= 3
    assert "Network" in groups
    assert groups["Network"]["count"] == 0
