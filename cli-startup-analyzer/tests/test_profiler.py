import pytest
from cli_startup_analyzer.profiler import profile_startup, ProfileResult

def test_profile_runs():
    r = profile_startup("echo hi", 2)
    assert r.runs == 2
    assert r.median_wall_ms > 0

def test_render_text():
    r = ProfileResult("echo", 1, 5.0, 6.0, [])
    assert "Median" in r.render("text")

def test_render_md():
    r = ProfileResult("echo", 1, 5.0, 6.0, [("os", 1.2)])
    assert "|" in r.render("md")

def test_json_roundtrip():
    r = ProfileResult("echo", 1, 5.0, 6.0, [])
    assert "target" in r.json()

def test_edge_empty_command():
    with pytest.raises(Exception):
        profile_startup("", 1)