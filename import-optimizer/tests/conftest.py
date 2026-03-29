import libcst as cst
import pytest
from pathlib import Path


@pytest.fixture
def parse_module():
    def _parse(code: str) -> cst.Module:
        return cst.parse_module(code)
    return _parse


@pytest.fixture
def tmp_py_file(tmp_path: Path, code: str):
    p = tmp_path / "test.py"
    p.write_text(code)
    return p