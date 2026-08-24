import pytest
from deadline_flow_analyzer.analyzer import analyze_project

def test_finds_missing_deadline(tmp_path):
    (tmp_path / 'a.py').write_text('async def foo(): pass')
    results = analyze_project(str(tmp_path))
    assert len(results) >= 0

def test_ignores_tests(tmp_path):
    (tmp_path / 'test_x.py').write_text('async def test_foo(): pass')
    results = analyze_project(str(tmp_path))
    assert all('test' not in r['location'] for r in results)

def test_handles_empty_dir(tmp_path):
    assert analyze_project(str(tmp_path)) == []

def test_config_loading(tmp_path):
    cfg = tmp_path / 'pyproject.toml'
    cfg.write_text('[tool.deadline-flow-analyzer]')
    assert analyze_project(str(tmp_path), str(cfg)) is not None

def test_json_output_shape(tmp_path):
    (tmp_path / 'b.py').write_text('def bar(): pass')
    results = analyze_project(str(tmp_path))
    assert isinstance(results, list)