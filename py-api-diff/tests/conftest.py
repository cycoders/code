import pytest


@pytest.fixture(autouse=True)
def no_git_please(monkeypatch):
    """Mock git calls for unit tests."""
    def mock_git(*args, **kwargs):
        raise RuntimeError("Git mock not implemented")
    monkeypatch.setattr("subprocess.check_output", mock_git)