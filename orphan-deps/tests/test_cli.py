import pathlib
from typer.testing import CliRunner

import pytest
from orphan_deps.cli import app


class TestCLI:
    def test_check_help(self, runner: CliRunner):
        result = runner.invoke(app, ['--help'])
        assert result.exit_code == 0

    def test_check_sample(self, runner: CliRunner, sample_project: pathlib.Path):
        result = runner.invoke(app, ['check', str(sample_project)])
        assert result.exit_code == 0
        assert 'unused' in result.stdout

    def test_prune_dry(self, runner: CliRunner, sample_project: pathlib.Path):
        result = runner.invoke(
            app, ['prune', str(sample_project), '-r', 'requirements.txt', '--dry-run']
        )
        assert result.exit_code == 0
        assert 'DRY-RUN' in result.stdout

    @pytest.mark.parametrize('flag', ['--yes', '-y'])
    def test_prune_yes(self, runner: CliRunner, sample_project: pathlib.Path, flag: str):
        result = runner.invoke(
            app,
            ['prune', str(sample_project), '-r', 'requirements.txt', flag],
            input='y\n',
        )
        assert result.exit_code == 0