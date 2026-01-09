import json
import pytest
from pathlib import Path

import yaml
import tomlkit

from config_merger_cli.loader import detect_format, load_config


@pytest.fixture
def tmp_config(tmp_path: Path, config_type: str):
    p = tmp_path / f"test.{config_type}"
    if config_type == 'yaml':
        p.write_text("a: 1\nb: {c: true, d: [1,2]}")
    elif config_type == 'json':
        p.write_text(json.dumps({'a': 1, 'b': {'c': True, 'd': [1,2]}}))
    elif config_type == 'toml':
        p.write_text("a = 1\n[b]\nc = true\n[[b.d]] d=1\n[[b.d]] d=2")
    return p


class TestLoader:
    @pytest.mark.parametrize("ext,expected", [('.yaml', 'yaml'), ('.yml', 'yaml'), ('.json', 'json'), ('.toml', 'toml')])
    def test_detect_format(self, tmp_path: Path, ext: str, expected: str):
        (tmp_path / f'test{ext}').touch()
        assert detect_format(str(tmp_path / f'test{ext}')) == expected

    @pytest.mark.parametrize("config_type", ['yaml', 'json', 'toml'])
    def test_load_config(self, tmp_config, config_type: str):
        data = load_config(str(tmp_config))
        assert data == {'a': 1, 'b': {'c': True, 'd': [1, 2]}}

    def test_load_invalid_ext(self):
        with pytest.raises(ValueError, match="Unsupported extension '.txt'"):
            detect_format('test.txt')

    def test_load_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_config(str(tmp_path / 'missing.yaml'))