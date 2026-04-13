def format_bytes(size: int) -> str:
    """Format bytes to human readable."""
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if abs(size) < 1024.0:
            return f"{size:,.1f} {unit}"
        size /= 1024.0
    return f"{size:,.1f} EiB"


def format_percent(value: float, total: float) -> str:
    """Format percentage."""
    if total == 0:
        return "0.0%"
    pct = (value / total) * 100
    return f"{pct:.1f}%"