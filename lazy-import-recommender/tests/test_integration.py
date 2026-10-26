def test_full_flow(tmp_path):
    (tmp_path / 'a.py').write_text('import json\ndef f(): pass')
    from lazy_import_recommender.scanner import scan_project
    assert scan_project(str(tmp_path))