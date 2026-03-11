from typing import List


def resample(values: List[float], num_bins: int = 50) -> List[float]:
    """Resample values into num_bins averages."""
    n = len(values)
    if n <= num_bins:
        return values + [0.0] * (num_bins - n)
    bin_size = n // num_bins
    resampled = []
    for i in range(num_bins):
        start = i * bin_size
        end = start + bin_size if i < num_bins - 1 else n
        if start < end:
            avg = sum(values[start:end]) / (end - start)
        else:
            avg = 0.0
        resampled.append(avg)
    return resampled


def render_sparkline(values: List[int], width: int = 80, height: int = 1) -> str:
    """Render values as unicode sparkline."""
    if not values:
        return " " * width
    # For height=1
    vals = [float(v) for v in values]
    resampled = resample(vals, width)
    chars = " ▁▂▃▄▅▆▇█"
    line = "".join(chars[int(v * (len(chars) - 1))] for v in resampled)
    return line
