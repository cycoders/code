from typing import Any


def parse_duration(value: str) -> float:
    """Parse duration string to seconds. Supports ms, s."""
    value = value.strip().lower()
    if value.endswith('ms'):
        return float(value[:-2]) / 1000.0
    if value.endswith('s'):
        return float(value[:-1])
    return float(value)


def parse_bw(value: str) -> float:
    """Parse bandwidth to kbps. Supports numbers, inf, kbps."""
    value = value.strip().lower()
    if value in ('inf', 'infty'):
        return float('inf')
    if value.endswith('kbps'):
        return float(value[:-4])
    return float(value)


assert parse_duration('100ms') == 0.1
assert parse_duration('1s') == 1.0
assert parse_duration('0.5') == 0.5
assert parse_bw('100') == 100.0
assert parse_bw('inf') == float('inf')
