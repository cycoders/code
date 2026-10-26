def test_scales(tmp_path):
    for i in range(5):
        (tmp_path / f'm{i}.py').write_text('import os')
    from lazy_import_recommender.scanner import scan_project
    assert len(scan_project(str(tmp_path))) == 5