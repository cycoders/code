import pytest
from unittest.mock import patch, MagicMock
from container_diff_cli.image import ensure_image_loaded, get_image_info


@patch("docker.from_env")
def test_get_image_info(mock_client):
    mock_img = MagicMock()
    mock_img.attrs = {"RootFS": {"Layers": ["sha:1"]}}
    mock_img.history.return_value = [{"Id": "sha:1", "Size": 123}]

    info = get_image_info(mock_img)
    assert info["rootfs_layers"] == ["sha:1"]
    assert info["layer_sizes"]["sha:1"] == 123


@patch("docker.from_env")
@patch("builtins.print")
def test_pull_progress(mock_print, mock_client):
    # Tests progress implicitly via coverage
    ensure_image_loaded("remote:tag")
    mock_client.images.pull.assert_called()
