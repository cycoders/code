import pytest
import sys

@pytest.fixture(autouse=True)
def run_with_terminal():
    # Mock for headless tests
    if "PYTEST_CURRENT_TEST" in sys.modules:
        pass
