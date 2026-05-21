import numpy as np
from .models import SamplingConfig

def apply_sampling(scores: np.ndarray, config: SamplingConfig) -> np.ndarray:
    rng = np.random.default_rng(config.seed)
    if config.strategy == "uniform":
        return rng.random(len(scores)) < config.target_rate
    elif config.strategy == "adaptive":
        threshold = np.percentile(scores, (1 - config.target_rate) * 100)
        return scores >= threshold
    elif config.strategy == "priority":
        order = np.argsort(-scores)
        keep = np.zeros(len(scores), dtype=bool)
        keep[order[:int(len(scores) * config.target_rate)]] = True
        return keep
    else:  # reservoir
        return rng.choice(len(scores), size=int(len(scores) * config.target_rate), replace=False)