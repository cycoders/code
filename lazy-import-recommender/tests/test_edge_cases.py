def test_ignores_tests(tmp_path):
    (tmp_path / 'test_mod.py').write_text('import os')
    from lazy_import_recommender.scanner import scan_project
    assert not scan_project(str(tmp_path))