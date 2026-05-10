import pytest
from pathlib import Path


@pytest.fixture
def sample_py_file(tmp_path: Path):
    py_file = tmp_path / "test.py"
    py_file.write_text('''
import os
if os.getenv("FF_USER_LOGIN"):
    pass
flag = os.getenv("FF_DARK_MODE")
''')
    return py_file


@pytest.fixture
def sample_js_file(tmp_path: Path):
    js_file = tmp_path / "test.js"
    js_file.write_text('''
const enabled = process.env["FF_FEATURE"];
FF.isEnabled("ff_test");
''')
    return js_file
