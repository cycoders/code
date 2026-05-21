from log_sampling_optimizer.models import SamplingConfig, LogRecord

def test_sampling_config_defaults():
    cfg = SamplingConfig()
    assert cfg.target_rate == 0.1
    assert cfg.strategy == "adaptive"

def test_log_record_validation():
    r = LogRecord(timestamp=1.0, level="ERROR", message="boom")
    assert r.level == "ERROR"