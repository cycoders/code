import pytest

@pytest.fixture
def sample_templates(tmp_path):
    (tmp_path / "safe.j2").write_text("{{ name }}")
    return tmp_path