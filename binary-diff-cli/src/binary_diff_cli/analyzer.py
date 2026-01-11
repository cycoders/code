import math
from collections import Counter
from io import BytesIO
from pathlib import Path
from typing import Tuple, List, Dict, Any


def entropy(hist: Counter, total: int) -> float:
    """Shannon entropy from byte histogram."""
    if total == 0:
        return 0.0
    res = 0.0
    for count in hist.values():
        p = count / total
        if p > 0:
            res -= p * math.log2(p)
    return res


def byte_histogram(path: Path, sample_size: int = 1024*1024) -> Counter:
    """Byte frequency counter (sampled)."""
    hist = Counter()
    buf = bytearray(4096)
    total_read = 0
    with open(path, "rb") as f:
        while chunk := f.readinto(buf):
            hist.update(buf[:chunk])
            total_read += chunk
            if sample_size and total_read >= sample_size:
                break
    return hist


def compute_stats(
    path1: Path, path2: Path, sample_bytes: int
) -> Dict[str, Any]:
    """Full stats."""
    size1 = os.path.getsize(path1)
    size2 = os.path.getsize(path2)

    # Changed bytes (full scan, efficient)
    changed = 0
    total_compared = min(size1, size2)
    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        f1.seek(0)
        f2.seek(0)
        while True:
            b1 = f1.read(1)
            b2 = f2.read(1)
            if not b1 or not b2:
                break
            if b1 != b2:
                changed += 1

    change_pct = changed / total_compared if total_compared > 0 else 0

    # Histograms
    hist1 = byte_histogram(path1, sample_bytes)
    hist2 = byte_histogram(path2, sample_bytes)
    total1 = sum(hist1.values())
    total2 = sum(hist2.values())
    ent1 = entropy(hist1, total1)
    ent2 = entropy(hist2, total2)

    def top_bytes(hist: Counter, total: int, n: int = 5) -> List[Tuple[int, int, float]]:
        return sorted(((b, hist[b], hist[b]/total) for b in hist), key=lambda x: x[1], reverse=True)[:n]

    return {
        "size1": size1,
        "size2": size2,
        "size_delta": size1 - size2,
        "changed": changed,
        "change_pct": change_pct,
        "entropy1": ent1,
        "entropy2": ent2,
        "entropy_delta": ent1 - ent2,
        "top1": top_bytes(hist1, total1),
        "top2": top_bytes(hist2, total2),
    }


def entropy_bars(
    path: Path,
    window: int = 4096,
    num_bars: int = 80,
    height: int = 20,
) -> str:
    """Generate ASCII entropy heatmap."""
    entropies: List[float] = []
    buf = bytearray()
    with open(path, "rb") as f:
        while len(entropies) < num_bars * 4:
            data = f.read(window // 4)
            if not data:
                break
            buf.extend(data)
            if len(buf) >= window:
                buf = buf[-(window):]
                hist = Counter(buf)
                e = entropy(hist, len(buf))
                entropies.append(e)

    if not entropies:
        return "[empty file]"

    step = max(1, len(entropies) // num_bars)
    entropies = entropies[::step][:num_bars]

    min_e, max_e = min(entropies), max(entropies)
    range_e = max_e - min_e + 1e-9

    bars = []
    for e in entropies:
        h = int(((e - min_e) / range_e) * height)
        bar = "█" * h + "░" * (height - h)
        bars.append(bar)

    return "\n".join(bars)