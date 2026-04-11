"""Pytest fixtures."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_unicodedata(mocker):
    """Mock unicodedata for tests."""
    mocker.patch("unicodedata.name")
    mocker.patch("unicodedata.category")
    mocker.patch("unicodedata.block")
    mocker.patch("unicodedata.bidirectional")
    mocker.patch("unicodedata.mirrored")
    mocker.patch("unicodedata.decomposition")
    mocker.patch("unicodedata.east_asian_width")
