import pytest

@pytest.fixture
def sample_project(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="demo"\nversion="0.1"')
    return tmp_path