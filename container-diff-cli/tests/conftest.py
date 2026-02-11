import pytest
import docker
from unittest.mock import MagicMock


@pytest.fixture
def mock_client(monkeypatch):
    mock_img1 = MagicMock()
    mock_img1.attrs = {
        "Size": 7200000,
        "Os": "linux",
        "Architecture": "amd64",
        "RootFS": {"Layers": ["sha256:abc123", "sha256:def456"]},
        "Config": {"Env": ["PATH=/bin"], "Labels": {"foo": "bar"}},
    }
    mock_img1.history.return_value = [
        {"Id": "sha256:abc123", "Size": 1000000},
        {"Id": "sha256:def456", "Size": 2000000},
    ]

    mock_img2 = MagicMock()
    mock_img2.attrs = {
        "Size": 7500000,
        "Os": "linux",
        "Architecture": "amd64",
        "RootFS": {"Layers": ["sha256:abc123", "sha256:ghi789"]},
        "Config": {"Env": ["PATH=/usr/bin", "NEW=val"], "Labels": {"foo": "bar"}},
    }
    mock_img2.history.return_value = [
        {"Id": "sha256:abc123", "Size": 1000000},
        {"Id": "sha256:ghi789", "Size": 2500000},
    ]

    mock_client = MagicMock()
    mock_client.images.get.return_value = mock_img1
    mock_client.images.pull.return_value = None

    monkeypatch.setattr("container_diff_cli.image.client", mock_client)
    monkeypatch.setattr("container_diff_cli.image.ensure_image_loaded", lambda n: mock_img1 if "1" in n else mock_img2)

    return mock_client
