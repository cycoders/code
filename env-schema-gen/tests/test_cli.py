import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from env_schema_gen.cli import app

runner = CliRunner()


def test_scan_cli(sample_project):
    result = runner.invoke(app, ['scan', str(sample_project)])
    assert result.exit_code == 0
    vars_path = Path('vars.json')
    assert vars_path.exists()
    data = json.loads(vars_path.read_text())
    assert data['summary']['total_vars'] == 5
    vars_path.unlink()


def test_generate_cli(sample_project):
    result = runner.invoke(app, ['generate', str(sample_project)])
    assert result.exit_code == 0
    assert Path('env_schema.py').exists()
    assert Path('ENV_VARS.md').exists()
    assert Path('.env.example').exists()


def test_validate_good(sample_project, monkeypatch):
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('PORT', '8000')
    result = runner.invoke(app, ['validate', str(sample_project)])
    assert result.exit_code == 0


def test_validate_bad(sample_project, monkeypatch):
    monkeypatch.setenv('PORT', 'not_an_int')
    result = runner.invoke(app, ['validate', str(sample_project)])
    assert result.exit_code == 1
    assert 'ValidationError' in result.stdout