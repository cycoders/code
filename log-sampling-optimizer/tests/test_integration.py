from log_sampling_optimizer.models import SamplingConfig
from log_sampling_optimizer.analyzer import compute_importance
from log_sampling_optimizer.strategies import apply_sampling

def test_full_pipeline():
    records = [type("R", (), {"level": "ERROR", "message": "e"})() for _ in range(50)]
    scores = compute_importance(records)
    mask = apply_sampling(scores, SamplingConfig(target_rate=0.2))
    assert mask.sum() >= 5