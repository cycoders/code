import sys
from unittest.mock import patch, MagicMock
from import_profiler.profiler import profile_imports


slow_loop = "total = sum(range(10000))\nimport os"


def test_profile_imports_simple(tmp_script):
    path = tmp_script("import os\nimport sys")
    data = profile_imports(path)

    modules = data["modules"]
    assert "os" in modules
    assert "sys" in modules
    assert data["total_startup_time"] > 0
    assert modules["os"]["inclusive"] > 0


@patch("builtins.__import__")
@patch("time.perf_counter")
def test_monkeypatch_timing(mock_time, mock_import, tmp_script):
    mock_time.side_effect = [0.0, 0.01, 0.02, 0.03]  # main->os:10ms, os->posix:10ms
    mock_import.return_value = MagicMock()
    mock_import.side_effect = lambda name, *a, **k: sys.modules.setdefault(name, MagicMock())

    path = tmp_script("import os")
    data = profile_imports(path)

    assert data["modules"]["os"]["inclusive"] == 0.01


@patch("time.perf_counter")
def test_exclusive_calc(tmp_script):
    path = tmp_script(slow_loop)
    data = profile_imports(path)

    modules = data["modules"]
    # __main__ excl high (loop), os incl low
    assert modules["__main__"]["exclusive"] > modules.get("os", {}).get("inclusive", 0)
    assert modules["os"]["exclusive"] >= 0


def test_error_handling(tmp_script):
    path = tmp_script("invalid syntax")

    try:
        profile_imports(path)
    except ValueError:
        pass
    else:
        assert False, "Should raise SyntaxError"
