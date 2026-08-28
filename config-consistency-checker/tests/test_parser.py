import pytest
from config_consistency_checker.parser import load_config

def test_load_yaml(tmp_path):
    p = tmp_path / 't.yaml'
    p.write_text('key: value')
    assert load_config(p)['key'] == 'value'