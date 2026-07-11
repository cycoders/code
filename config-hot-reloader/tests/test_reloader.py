import tempfile
from pathlib import Path

import pytest
from config_hot_reloader import ConfigReloader

def test_load_valid_yaml():
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        f.write(b'port: 8080\n')
        path = Path(f.name)
    r = ConfigReloader(path)
    assert r.current['port'] == 8080


def test_validator_rejects_bad_config():
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        f.write(b'port: "notanint"\n')
        path = Path(f.name)
    def v(c): assert isinstance(c['port'], int)
    with pytest.raises(AssertionError):
        ConfigReloader(path, validator=v)


def test_atomic_update(tmp_path):
    cfg = tmp_path / 'cfg.yaml'
    cfg.write_text('a: 1\n')
    r = ConfigReloader(cfg)
    assert r.current['a'] == 1
    cfg.write_text('a: 2\n')
    # simulate event
    r._load()
    assert r.current['a'] == 2