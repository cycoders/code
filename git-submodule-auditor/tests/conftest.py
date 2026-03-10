import pytest

@pytest.fixture
 def mock_repo(mocker):
    """Mock Git Repo for tests."""
    mock_sm = mocker.Mock(path="test/sub", hexsha="a1b2c3d4e5f678901234567890123456789abcd", branch=mocker.Mock(name="main"), url="https://github.com/example/repo.git")
    mock_repo = mocker.Mock(submodules=[mock_sm], git=mocker.Mock())
    mocker.patch('git_submodule_auditor.auditor.git.Repo', return_value=mock_repo)
    return mock_repo
