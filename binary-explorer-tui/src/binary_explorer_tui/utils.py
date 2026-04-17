import math
from collections import Counter
from typing import Union


def entropy(data: bytes) -> float:
    """Shannon entropy of bytes (0-8). >7 suggests compressed/packed."""
    if not data:
        return 0.0
    counter = Counter(data)
    length = len(data)
    ent = 0.0
    for count in counter.values():
        p_x = count / length
        ent -= p_x * math.log2(p_x)
    return ent


def human_size(size: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


def hex_addr(addr: int) -> str:
    return f"0x{addr:016x}"
