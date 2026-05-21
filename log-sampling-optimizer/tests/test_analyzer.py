from log_sampling_optimizer.models import LogRecord
from log_sampling_optimizer.analyzer import compute_importance
import numpy as np

def test_importance_scores():
    records = [LogRecord(timestamp=0, level=lvl, message="x") for lvl in ["INFO", "ERROR", "CRITICAL"]]
    scores = compute_importance(records)
    assert len(scores) == 3
    assert np.all(scores >= 0)