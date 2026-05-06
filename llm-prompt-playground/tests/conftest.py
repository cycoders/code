import pytest
import sys

sys.path.insert(0, "..")


@pytest.fixture(autouse=True)
def setup():
    pass
