from numeric_tolerance_analyzer.config import Config

def test_default_config():
    cfg = Config()
    assert cfg.min_tol == 1e-12