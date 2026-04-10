import pytest
import pathlib
from local_hosts_manager.hosts import HostsManager

@pytest.fixture
def mock_hosts_path(tmp_path: pathlib.Path, monkeypatch):
    def mock_get_path():
        return tmp_path / "hosts"
    monkeypatch.setattr("local_hosts_manager.hosts.HostsManager._get_hosts_path", mock_get_path)
    return tmp_path / "hosts"