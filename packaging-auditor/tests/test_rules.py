from packaging_auditor.rules import check_metadata

def test_name_required():
    assert any("name" in f["message"] for f in check_metadata({}, Path(".")))

def test_readme_warning():
    data = {"project": {"name": "x", "version": "1"}}
    res = check_metadata(data, Path("."))
    assert any("readme" in f["message"] for f in res)