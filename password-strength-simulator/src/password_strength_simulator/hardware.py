"""
Hardware benchmark speeds (log10 H/s) calibrated to Hashcat 2024.
Sources: https://hashcat.net/hashcat/wiki/doku.php?id=benchmark
RTX 4090, i9-13900K, etc.
"""

import math

from typing import Dict, Any


SPEEDS_LOG10: Dict[str, Dict[str, float]] = {
    "md5": {
        "cpu-i9": 10.18,  # 15 GH/s
        "rtx4090": 11.39,  # 246 GH/s
        "100-gpu-cluster": 13.39,
        "top-super": 15.0,
    },
    "sha1": {
        "cpu-i9": 9.95,  # 8.9 GH/s
        "rtx4090": 11.15,  # 141 GH/s
        "100-gpu-cluster": 13.15,
        "top-super": 14.8,
    },
    "pbkdf2-sha256": {
        "cpu-i9": 8.0,  # 1 GH/s @ 310k iters -> adjust
        "rtx4090": 9.3,  # 20 GH/s @310k
        "100-gpu-cluster": 11.3,
        "top-super": 13.0,
    },
    "bcrypt": {
        "cpu-i9": 4.45,  # 28 kH/s @ cost12
        "rtx4090": 5.33,  # 215 kH/s @12
        "100-gpu-cluster": 7.33,
        "top-super": 9.0,
    },
    "scrypt": {
        "cpu-i9": 7.3,  # 2e7 @ N=4096
        "rtx4090": 8.6,
        "100-gpu-cluster": 10.6,
        "top-super": 12.0,
    },
    "argon2": {
        "cpu-i9": 6.48,  # 3 MH/s
        "rtx4090": 7.65,  # 45 MH/s
        "100-gpu-cluster": 9.65,
        "top-super": 11.0,
    },
}

ALGO_BASE_COST = {
    "bcrypt": 12,
    "pbkdf2-sha256": 100000,
    "scrypt": 4096,
    "argon2": 1,
}

ALGO_COST_TYPE = {
    "md5": "none",
    "sha1": "none",
    "bcrypt": "pow2",
    "pbkdf2-sha256": "iter",
    "scrypt": "iter",
    "argon2": "iter",
}


HARDWARES = list(SPEEDS_LOG10["md5"].keys())


def get_log10_speed(algo: str, cost: int, hardware: str) -> float:
    """Get log10(hashes/sec) adjusted for cost."""
    if algo not in SPEEDS_LOG10:
        raise ValueError(f"Unknown algo: {algo}")
    if hardware not in SPEEDS_LOG10[algo]:
        raise ValueError(f"Unknown hardware: {hardware}")

    base_log10 = SPEEDS_LOG10[algo][hardware]
    cost_type = ALGO_COST_TYPE.get(algo, "none")

    if cost_type == "none":
        return base_log10

    base_cost = ALGO_BASE_COST.get(algo, 1)
    if cost_type == "pow2":
        factor = 2 ** (cost - base_cost)
    else:  # iter
        factor = cost / base_cost

    return base_log10 - math.log10(factor)


def list_hardware() -> list[str]:
    return HARDWARES


def list_algos() -> list[str]:
    return list(SPEEDS_LOG10.keys())