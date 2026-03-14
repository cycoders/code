import pytest
from pathlib import Path

from curl_history_analyzer.parser import parse_history_file
from curl_history_analyzer.models import CurlHistoryEntry


@pytest.fixture
def sample_file() -> Path:
    return Path(__file__).parent / "data" / "sample.jsonl"


def test_parse_valid(sample_file: Path) -> None:
    entries = parse_history_file(sample_file)
    assert len(entries) == 6
    assert all(isinstance(e, CurlHistoryEntry) for e in entries)
    assert entries[0].url_effective == "https://api.github.com/users/octocat"
    assert entries[0].is_error is False
    assert entries[2].is_error is True


def test_nonexistent_file(tmp_path: Path) -> None:
    with pytest.raises(typer.Exit):
        parse_history_file(tmp_path / "missing.jsonl")


def test_invalid_lines(sample_file: Path) -> None:
    # Append invalid
    invalid = sample_file.read_text() + "\ninvalid json"
    bad_file = Path(sample_file).with_suffix(".bad.jsonl")
    bad_file.write_text(invalid)
    entries = parse_history_file(bad_file)
    assert len(entries) == 6  # skipped 1