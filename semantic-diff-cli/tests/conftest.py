'''Pytest fixtures.''' 

import pytest


@pytest.fixture
def mock_console(mocker):
    """Mock rich console."""
    return mocker.patch("rich.console.Console")
