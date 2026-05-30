from typing import List, Dict
import numpy as np
from scipy import stats

def analyze(sources: List[str], key: str, ts_field: str) -> Dict:
    events = []
    # streaming parse omitted for brevity; returns list of (node, ts, key)
    for src in sources:
        # ... parse logic ...
        pass
    # pairwise Theil-Sen estimator
    skews = {}
    # ... compute robust skews ...
    return {"skews": skews, "n_events": len(events)}