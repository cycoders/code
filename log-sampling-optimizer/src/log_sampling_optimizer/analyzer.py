import numpy as np
from collections import Counter
from .models import LogRecord, SamplingConfig

def compute_importance(records: list[LogRecord]) -> np.ndarray:
    levels = [r.level for r in records]
    level_weights = {"DEBUG": 0.1, "INFO": 0.3, "WARNING": 0.7, "ERROR": 0.95, "CRITICAL": 1.0}
    weights = np.array([level_weights[l] for l in levels])
    # Add burst and cardinality signals
    msg_hashes = [hash(r.message) % 10000 for r in records]
    uniqueness = np.array([1.0 / (Counter(msg_hashes)[h] + 1) for h in msg_hashes])
    return weights * 0.7 + uniqueness * 0.3