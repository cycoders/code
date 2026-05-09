import pytest
from unittest.mock import Mock, patch

from csp_policy_builder.scanner import Scanner
from csp_policy_builder.types import ScanConfig


@pytest.fixture
def sample_config():
    return ScanConfig(urls=["https://test.com"], max_depth=0, max_pages=1)


@pytest.fixture
def mock_session():
    session = Mock()
    session.get.return_value.text = open("tests/fixtures/sample.html").read()
    session.get.return_value.url = "https://test.com/"
    session.get.return_value.raise_for_status.return_value = None
    return session
