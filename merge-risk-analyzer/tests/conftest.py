import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_git_repo(tmp_path):
    """Mock GitRepo for tests."""
    repo_mock = Mock()
    repo_mock.git.merge_base.return_value = "deadbeef"
    repo_mock.git.rev_parse.return_value.hexsha = "abc123"
    (tmp_path / ".git").mkdir()
    return repo_mock
