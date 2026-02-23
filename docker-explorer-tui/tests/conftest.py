import pytest
from unittest.mock import Mock, MagicMock

from docker.models.containers import Container
from docker import DockerClient


@pytest.fixture
def mock_container() -> Container:
    cont = MagicMock(spec=Container)
    cont.id = "deadbeef1234567890abcdef1234567890abcdef"
    cont.name = "test-container"
    cont.image.tags = ["nginx:alpine"]
    cont.status = "Up 10 seconds"
    cont.ports = {"80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]}
    cont.attrs = {
        "Created": 1699123456,
        "Config": {"Cmd": ["/docker-entrypoint.sh", "nginx"]},
    }
    return cont


@pytest.fixture
def mock_client(mock_container) -> DockerClient:
    client = MagicMock(spec=DockerClient)
    client.ping.return_value = b"OK"
    client.containers.list.return_value = [mock_container]
    # Mock stats
    mock_stats = MagicMock()
    mock_stats.__aiter__ = MagicMock()
    mock_stats.__anext__ = MagicMock(return_value={
        "cpu_stats": {
            "cpu_usage": {"total_usage": 50000, "percpu_usage": [10000, 15000]},
            "system_cpu_usage": 1000000,
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 0, "percpu_usage": [0, 0]},
            "system_cpu_usage": 0,
        },
        "memory_stats": {"usage": 134217728, "limit": 1073741824},
        "networks": {},
    })
    mock_container.stats.return_value = mock_stats()
    mock_container.logs.return_value = b"2024-01-01T00:00:00Z test log\n"
    return client