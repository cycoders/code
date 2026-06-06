import math

def optimal_params(n: int, p: float) -> tuple[int, int]:
    """Return (m, k) for given cardinality and false-positive rate."""
    if not (0 < p < 1):
        raise ValueError("fp rate must be in (0,1)")
    m = math.ceil(-(n * math.log(p)) / (math.log(2) ** 2))
    k = math.ceil((m / n) * math.log(2))
    return m, max(k, 1)