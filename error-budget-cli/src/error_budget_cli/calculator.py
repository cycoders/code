from datetime import timedelta

def remaining_budget(target: float, total: int, bad: int) -> float:
    allowed = total * (1 - target / 100)
    return max(0.0, allowed - bad)

def burn_rate(bad: int, total: int, window_seconds: int) -> float:
    if total == 0:
        return 0.0
    return (bad / total) / (window_seconds / 3600)

def hours_to_exhaustion(remaining: float, burn_rate_per_hour: float) -> float | None:
    if burn_rate_per_hour <= 0:
        return None
    return remaining / burn_rate_per_hour