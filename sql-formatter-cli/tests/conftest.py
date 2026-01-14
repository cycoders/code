'''Pytest fixtures.''' 

import pytest
from sql_formatter_cli.config import DEFAULTS


@pytest.fixture
def default_config():
    """Default config."""
    return DEFAULTS.copy()
