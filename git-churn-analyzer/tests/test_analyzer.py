import pytest
from datetime import datetime, timedelta, timezone

from git_churn_analyzer.analyzer import analyze_commits
from git_churn_analyzer.models import FileChurn, GitCommit, GitFileChange


@pytest.fixture
def sample_commits():
    dt1 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    dt2 = datetime(2024, 10, 1, tzinfo=timezone.utc)
    c1 = GitCommit("sha1", dt1, "auth1", "msg", [GitFileChange("f1", 10, 2), GitFileChange("f2", 0, 5)])
    c2 = GitCommit("sha2", dt2, "auth2", "msg", [GitFileChange("f1", 3, 1)])
    recent_dt = datetime.now(timezone.utc) - timedelta(days=15)
    c3 = GitCommit("sha3", recent_dt, "auth1", "msg", [GitFileChange("f1", 20, 10)])
    return [c1, c2, c3]


def test_analyze_commits(sample_commits):
    stats = analyze_commits(sample_commits, recent_days=30)
    assert stats["total_commits"] == 3
    top_files = stats["top_files"]
    assert len(top_files) == 2
    f1 = next(f for f in top_files if f.path == "f1")
    assert f1.total_churn == 46  # 12 + 4 + 30
    assert f1.recent_churn == 30
    assert f1.commit_count == 3
    assert f1.top_author == "auth1"
    assert f1.top_author_churn == 40  # 12 + 30
    assert f1.last_commit == sample_commits[2].timestamp

    authors = stats["top_authors"]
    assert authors[0][0] == "auth1"
    assert authors[0][1] == 42
