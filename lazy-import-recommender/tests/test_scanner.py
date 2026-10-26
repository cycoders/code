import pytest
from lazy_import_recommender.scanner import scan_project

def test_finds_imports(tmp_path):
    (tmp_path / 'mod.py').write_text('import os\nimport sys')
    res = scan_project(str(tmp_path))
    assert any('mod.py' in r for r in res)