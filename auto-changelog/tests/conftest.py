import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_repo(mocker):
    """Mock git Repo."""
    mock_repo = Mock()
    mocker.patch("auto_changelog.parser.Repo", return_value=mock_repo)
    return mock_repo