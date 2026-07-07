import pytest

@pytest.fixture
def sample_code(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text("a = sum(x) + (b == c)")
    return tmp_path