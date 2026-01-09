import pytest
from config_merger_cli.cli import app
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_help(self, runner):
        result = runner.invoke(app, ['--help'])
        assert result.exit_code == 0
        assert 'Merge layered config files' in result.stdout

    def test_no_args(self, runner):
        result = runner.invoke(app)
        assert result.exit_code == 2  # typer usage
        assert 'Provide at least one config file' in result.stderr

    @pytest.fixture
    def sample_configs(self, tmp_path):
        base = tmp_path / 'base.yaml'
        base.write_text('''
service:
  port: 8080
  tags: [prod]
''')
        dev = tmp_path / 'dev.yaml'
        dev.write_text('''
service:
  debug: true
  tags: [dev]
''')
        return base, dev

    def test_merge_basic(self, runner, sample_configs, tmp_path):
        base, dev = sample_configs
        out = tmp_path / 'merged.yaml'
        result = runner.invoke(app, ['merge', str(base), str(dev), '--output', str(out)])
        assert result.exit_code == 0
        import yaml
        with open(out) as f:
            merged = yaml.safe_load(f)
        assert merged == {
            'service': {'port': 8080, 'tags': ['prod', 'dev'], 'debug': True}
        }

    def test_strategy_union(self, runner, sample_configs):
        base, dev = sample_configs
        result = runner.invoke(
            app, ['merge', str(base), str(dev), '--strategy', 'lists=union']
        )
        import yaml
        merged = yaml.safe_load(result.stdout)
        assert merged['service']['tags'] == ['prod', 'dev']

    def test_env_override(self, runner, sample_configs, monkeypatch):
        monkeypatch.setenv('APP__SERVICE__PORT', '9999')
        base, _ = sample_configs
        result = runner.invoke(
            app,
            ['merge', str(base), '--env-prefix', 'APP_', '--format', 'json'],
        )
        assert result.exit_code == 0
        import json
        merged = json.loads(result.stdout)
        assert merged['service']['port'] == 9999

    def test_error_file_not_found(self, runner, tmp_path):
        result = runner.invoke(app, ['merge', 'missing.yaml'])
        assert result.exit_code == 1
        assert 'not found' in result.stderr