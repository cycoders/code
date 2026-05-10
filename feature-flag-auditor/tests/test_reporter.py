import pytest
from pathlib import Path

from feature_flag_auditor.types import Usage
from feature_flag_auditor.reporter import Report


@pytest.fixture
def sample_usages(tmp_path: Path):
    p1 = tmp_path / "f1.py"
    p1.touch()
    p2 = tmp_path / "f2.py"
    p2.touch()
    return [
        Usage(p1, 10, "FF_A", "os.getenv('FF_A')"),
        Usage(p1, 20, "FF_B", "os.getenv('FF_B')"),
        Usage(p2, 5, "FF_A", "os.getenv('FF_A')"),
    ]


def test_report_stats(sample_usages):
    report = Report(sample_usages)
    assert report.stats["total_usages"] == 3
    assert report.stats["unique_flags"] == 2
    assert report.stats["files_touched"] == 2


def test_dead_unknown_flags(sample_usages):
    active = {"FF_A", "FF_DEAD"}
    report = Report(sample_usages, active)
    assert "FF_DEAD" in report.dead_flags
    assert "FF_B" in report.unknown_flags


def test_markdown_contains_flags(sample_usages):
    report = Report(sample_usages)
    md = report.markdown_report()
    assert "FF_A" in md
    assert "| 2 | 1 |" in md
