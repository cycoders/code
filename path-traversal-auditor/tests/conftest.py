import pytest

@pytest.fixture
def sample_code():
    return 'f = open(request.args["file"])'