import numpy as np
from scipy import stats
from .models import LatencyHistogram, TimeoutRecommendation

def fit_and_recommend(hist: LatencyHistogram, slo: float = 0.999, budget: float = 0.01) -> TimeoutRecommendation:
    data = np.repeat(hist.buckets_ms, hist.counts)
    params = stats.lognorm.fit(data)
    p99 = stats.lognorm.ppf(0.99, *params)
    p999 = stats.lognorm.ppf(0.999, *params)
    timeout = min(p999 * 1.5, p99 * 3)
    slo_ok = (1 - stats.lognorm.cdf(timeout, *params)) >= slo - budget
    return TimeoutRecommendation(p99_ms=p99, p999_ms=p999, recommended_timeout_ms=timeout, confidence="high", slo_compliant=slo_ok)