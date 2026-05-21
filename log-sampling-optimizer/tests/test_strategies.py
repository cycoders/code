import numpy as np
from log_sampling_optimizer.models import SamplingConfig
from log_sampling_optimizer.strategies import apply_sampling

def test_uniform_keeps_ratio():
    scores = np.linspace(0, 1, 1000)
    mask = apply_sampling(scores, SamplingConfig(target_rate=0.2, strategy="uniform", seed=1))
    assert 180 <= mask.sum() <= 220

def test_adaptive_prefers_high_scores():
    scores = np.array([0.1, 0.9, 0.2, 0.95])
    mask = apply_sampling(scores, SamplingConfig(target_rate=0.5, strategy="adaptive"))
    assert mask[1] and mask[3]