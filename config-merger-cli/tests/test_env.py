import os
import pytest
from config_merger_cli.env import apply_env_overrides, _parse_value, set_nested


class TestEnv:
    def test_parse_value(self):
        assert _parse_value('true') is True
        assert _parse_value('1') is True
        assert _parse_value('false') is False
        assert _parse_value('0') is False
        assert _parse_value('null') is None
        assert _parse_value('42') == 42
        assert _parse_value('3.14') == 3.14
        assert _parse_value('hello') == 'hello'
        assert _parse_value('-inf') == float('-inf')

    def test_set_nested(self):
        config = {}
        set_nested(config, ['a', 'b', 'c'], 42)
        assert config == {'a': {'b': {'c': 42}}}

    def test_set_nested_existing(self):
        config = {'a': {'b': 1}}
        set_nested(config, ['a', 'b', 'c'], 42)
        assert config == {'a': {'b': {'c': 42}}}

    def test_apply_env_overrides(self, monkeypatch):
        monkeypatch.setenv('APP__SERVICE__PORT', '9999')
        monkeypatch.setenv('APP__DEBUG', 'false')
        config = {'service': {'port': 8080}, 'debug': True}
        apply_env_overrides(config, 'APP')
        assert config == {'service': {'port': 9999}, 'debug': False}

    def test_apply_no_prefix(self, monkeypatch):
        monkeypatch.setenv('NOPE', 'val')
        config = {}
        apply_env_overrides(config, 'APP')
        assert config == {}

    def test_apply_nested_deep(self, monkeypatch):
        monkeypatch.setenv('APP__X__Y__Z', '42')
        config = {'x': {}}
        apply_env_overrides(config, 'APP')
        assert config['x']['y']['z'] == 42