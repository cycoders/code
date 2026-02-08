import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_docker(monkeypatch):
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0
    monkeypatch.setattr("subprocess.run", mock_run)
    monkeypatch.setattr("subprocess.check_output", MagicMock())
    return mock_run

@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setattr("local_service_hub.config.load_config", lambda: {})
