import json
from pathlib import Path

import pytest
from git_churn_analyzer.output import print_terminal, render_stats, write_csv, write_html, write_json


@pytest.mark.parametrize("fmt", ["json", "csv", "html"])
def test_render_stats(tmp_path: Path, sample_stats, fmt: str):
    out_path = tmp_path / "test." + ("csv" if fmt == "csv" else "json" if fmt == "json" else "html")
    render_stats(sample_stats, fmt, out_path)
    assert out_path.exists()
    assert out_path.read_text().strip()


@pytest.fixture
def sample_stats():
    from git_churn_analyzer.models import FileChurn
    from datetime import datetime

    f1 = FileChurn("test.py", total_churn=100, recent_churn=20, commit_count=5, top_author="dev")
    f1.last_commit = datetime.now()
    return {"top_files": [f1], "top_authors": [("dev", 100)], "total_commits": 10, "total_churn": 100}


def test_terminal(capfd):
    sample_stats = {"top_files": [], "top_authors": [], "total_commits": 0}
    print_terminal(sample_stats)
    captured = capfd.readouterr()
    assert "Git Churn Analysis" in captured.out


def test_csv(tmp_path: Path, sample_stats):
    p = tmp_path / "test.csv"
    write_csv(p, sample_stats)
    content = p.read_text()
    assert "path,total_churn" in content


def test_json(tmp_path: Path, sample_stats):
    p = tmp_path / "test.json"
    write_json(p, sample_stats)
    content = json.loads(p.read_text())
    assert content["total_commits"] == 10


def test_html(tmp_path: Path, sample_stats):
    p = tmp_path / "test.html"
    write_html(p, sample_stats)
    content = p.read_text()
    assert "<table>" in content
    assert "test.py" in content
