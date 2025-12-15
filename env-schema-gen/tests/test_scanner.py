import json

from env_schema_gen.scanner import scan_directory


def test_scan_directory(sample_project):
    data = scan_directory(sample_project)
    vars_data = data['vars']
    assert len(vars_data) == 5
    assert 'DB_HOST' in vars_data
    assert vars_data['DB_HOST']['type'] == 'str'
    assert 'PORT' in vars_data
    assert vars_data['PORT']['type'] == 'int'
    assert 'DEBUG' in vars_data
    assert vars_data['DEBUG']['type'] == 'bool'
    assert data['summary']['total_files'] == 3


def test_gitignore_respected(sample_project):
    (sample_project / 'venv' / 'script.py').write_text('pass')
    (sample_project / '.gitignore').write_text('venv/')
    data = scan_directory(sample_project)
    assert data['summary']['total_files'] == 3  # excludes venv


def test_exclude_flag(sample_project):
    data = scan_directory(sample_project, exclude=['*.py'])
    assert data['summary']['total_files'] == 0