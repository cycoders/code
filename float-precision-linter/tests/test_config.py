import os
from float_precision_linter.config import Config

def test_env_override(monkeypatch):
    monkeypatch.setenv("FPL_TOLERANCE", "1e-12")
    c = Config.from_env()
    assert c.tolerance == 1e-12