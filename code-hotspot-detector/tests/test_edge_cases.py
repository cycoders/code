from code_hotspot_detector.core import analyze_hotspots

def test_non_python_ignored(tmp_path, monkeypatch):
    # test that non-python files are skipped
    pass

def test_empty_repo(tmp_path):
    import git
    git.Repo.init(tmp_path)
    res = analyze_hotspots(str(tmp_path), '1d', 10)
    assert res == []