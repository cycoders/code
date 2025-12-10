import pytest
from unittest.mock import Mock, patch
from auto_changelog.parser import parse_commits, Commit, NoConventionalCommits


@pytest.fixture
def mock_commits():
    commits = [
        Mock(message="feat(ui): add button (#123)\n\nResolves #456", hexsha="abc123"),
        Mock(message="fix!: critical bug", hexsha="def456"),
        Mock(message="chore(deps): bump", hexsha="ghi789"),
        Mock(message="invalid msg", hexsha="jkl012"),
        Mock(
            message="feat(api): endpoint\n\nBREAKING CHANGE: new schema",
            hexsha="mno345",
        ),
    ]
    return commits


def test_parse_commits(mock_repo, mock_commits):
    mock_repo.iter_commits.return_value = mock_commits

    commits = parse_commits(".", "v1.0.0", "HEAD")

    assert len(commits) == 4
    assert commits[0] == Commit("abc123", "feat", "ui", "add button (#123)", False)
    assert commits[1].breaking is True
    assert commits[1].scope is None
    assert commits[2].type_ == "chore"


def test_no_commits(mock_repo):
    mock_repo.iter_commits.return_value = []
    with pytest.raises(NoConventionalCommits):
        parse_commits(".", "a", "b")


def test_invalid_repo():
    with patch("auto_changelog.parser.Repo") as mock_repo:
        mock_repo.side_effect = Exception("bad repo")
        with pytest.raises(Exception):
            parse_commits("/bad", "a", "b")