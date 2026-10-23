import ast
from coroutine_lifetime_analyzer.analyzer import analyze_path

def test_detects_create_task(tmp_path):
    code = "import asyncio\nasync def main():\n    asyncio.create_task(some_coro())\n"
    f = tmp_path / "t.py"
    f.write_text(code)
    res = analyze_path(str(tmp_path))
    assert any("create_task" in r for r in res)

def test_ignores_normal_gather(tmp_path):
    code = "import asyncio\nasync def main():\n    await asyncio.gather(c1(), c2())\n"
    f = tmp_path / "t.py"
    f.write_text(code)
    res = analyze_path(str(tmp_path))
    assert res == []

def test_handles_empty_dir(tmp_path):
    assert analyze_path(str(tmp_path)) == []

def test_multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("asyncio.create_task(x())")
    (tmp_path / "b.py").write_text("pass")
    res = analyze_path(str(tmp_path))
    assert len(res) == 1

def test_edge_case_nested(tmp_path):
    code = "def outer():\n    def inner(): asyncio.create_task(y())\n"
    f = tmp_path / "t.py"
    f.write_text(code)
    res = analyze_path(str(tmp_path))
    assert len(res) == 1