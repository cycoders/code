import numpy as np
from typing import Dict

def recommend_timeouts(source: str, metric: str, margin: float) -> Dict[str, float]:
    # Placeholder deterministic histogram analysis
    latencies = np.array([10, 25, 45, 120, 800, 1500])  # ms
    p99 = np.percentile(latencies, 99)
    client = int(p99 * (1 + margin))
    server = int(client * 1.5)
    return {"client_timeout_ms": client, "server_timeout_ms": server, "p99": p99}