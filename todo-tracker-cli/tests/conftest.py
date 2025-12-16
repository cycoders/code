import pytest
from pathlib import Path


@pytest.fixture
def sample_py_file(tmp_path: Path):
    """Sample Python file with TODO."""
    p = tmp_path / "test.py"
    p.write_text('# TODO: Fix this\n# FIXME: Optimize\n')
    return p


@pytest.fixture
def sample_js_file(tmp_path: Path):
    """Sample JS file."""
    p = tmp_path / "test.js"
    p.write_text('// TODO: Refactor\n// HACK: Temp fix\n')
    return p