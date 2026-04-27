import pytest
from datetime import datetime, timezone
from git_blame_tui.parser import parse_blame_porcelain
from git_blame_tui.models import BlameEntry


class TestParser:
    def test_parse_single_block_single_line(self, sample_porcelain: str) -> None:
        entries = parse_blame_porcelain(sample_porcelain)
        assert len(entries) == 2
        entry = entries[0]
        assert entry.commit == "abc123def4567890abcdef1234567890abcde"
        assert entry.author == "John Doe"
        assert entry.content == 'def parse():'
        assert entry.lineno == 1

    def test_parse_multi_line_block(self, sample_porcelain: str) -> None:
        entries = parse_blame_porcelain(sample_porcelain)
        assert len(entries) == 2
        assert entries[1].lineno == 2
        assert "print" in entries[1].content

    def test_parse_multiple_blocks(self, sample_porcelain: str) -> None:
        entries = parse_blame_porcelain(sample_porcelain)
        assert len(entries) == 2
        assert entries[1].commit == "fedcba9876543210fedcba9876543210fedcba"

    def test_parse_boundary(self, sample_porcelain: str) -> None:
        entries = parse_blame_porcelain(sample_porcelain)
        assert len(entries) == 2  # Ignores boundary

    def test_parse_empty(self) -> None:
        entries = parse_blame_porcelain("")
        assert len(entries) == 0

    def test_parse_timestamp(self, sample_porcelain: str) -> None:
        entries = parse_blame_porcelain(sample_porcelain)
        dt = entries[0].author_time
        assert isinstance(dt, datetime)
        assert dt.tzinfo == timezone.utc  # Simplified

    def test_parse_prev_commit(self, sample_porcelain: str) -> None:
        entries = parse_blame_porcelain(sample_porcelain)
        assert entries[0].prev_commit == "abc123def4567890abcdef1234567890abcde"
