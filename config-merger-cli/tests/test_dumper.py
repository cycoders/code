import json
import pytest
from io import StringIO
from config_merger_cli.dumper import dump_config


class TestDumper:
    def test_dump_yaml(self, tmp_path):
        data = {'a': 1, 'b': [2, 3]}
        out = tmp_path / 'out.yaml'
        dump_config(data, str(out), 'yaml')
        with open(out) as f:
            assert yaml.safe_load(f) == data

    def test_dump_json(self, tmp_path):
        data = {'key': 'val', 'list': [1, 2]}
        out = tmp_path / 'out.json'
        dump_config(data, str(out), 'json')
        with open(out) as f:
            assert json.load(f) == data

    def test_dump_toml(self, tmp_path):
        data = {'a': 1, 'b': {'c': True}}
        out = tmp_path / 'out.toml'
        dump_config(data, str(out), 'toml')
        import tomlkit
        with open(out) as f:
            assert tomlkit.parse(f.read()).as_dict() == data

    def test_dump_stdout(self, capsys):
        data = {'hello': 'world'}
        dump_config(data, '-', 'json')
        captured = capsys.readouterr()
        assert json.loads(captured.out) == data

    def test_dump_invalid_fmt(self, tmp_path):
        with pytest.raises(ValueError, match="Unsupported output format"):
            dump_config({}, str(tmp_path), 'invalid')