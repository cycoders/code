import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

@pytest.fixture
def sample_ssh_dir(tmp_path: Path):
    dir_path = tmp_path / "ssh"
    dir_path.mkdir()
    return dir_path

@pytest.fixture
def mock_key_rsa_weak():
    mock_key = Mock()
    mock_key.public_numbers.return_value = Mock(n=Mock(bit_length=lambda: 1024))
    mock_key.public_bytes.return_value = b"fake"
    return mock_key

@pytest.fixture
def mock_key_ed25519():
    mock_key = Mock()
    mock_key.public_bytes.return_value = b"fake"
    return mock_key