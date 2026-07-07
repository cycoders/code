import ast
from float_precision_linter.analyzer import analyze_path

def test_detects_sum(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("total = sum(values)")
    assert len(analyze_path(str(tmp_path), 1e-9)) == 1

def test_ignores_safe_code(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("total = math.fsum(values)")
    assert len(analyze_path(str(tmp_path), 1e-9)) == 0

def test_tolerance_propagates(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("x == y")
    res = analyze_path(str(tmp_path), 1e-12)
    assert res[0]["line"] == 1