import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_resolver():
    mock = MagicMock()
    mock.configure_mock(**{"resolve.return_value": [MagicMock(__str__=lambda s: "mock")]})
    return mock