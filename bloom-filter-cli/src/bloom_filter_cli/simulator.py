import numpy as np
import yaml

def run(config_path: str) -> str:
    """Execute simulation and return summary."""
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    n = cfg["elements"]
    m, k = cfg["m"], cfg["k"]
    # Monte-Carlo using bit array approximation
    bits = np.zeros(m, dtype=bool)
    for _ in range(n):
        for h in range(k):
            idx = hash((_, h)) % m
            bits[idx] = True
    fp_est = (1 - (1 - bits.mean()) ** k)
    return f"estimated_fp={fp_est:.6f}"