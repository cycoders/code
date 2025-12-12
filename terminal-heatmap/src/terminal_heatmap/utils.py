"""
Utility functions for braille conversion and coloring.
"""

def value_to_braille(value: float, max_val: float = 100.0) -> str:
    """Convert 0-100 value to unicode braille block (U+2800 - U+28FF)."""
    clamped = min(value, max_val)
    intensity = int((clamped / max_val) * 255)
    return chr(0x2800 + intensity)


def get_intensity_color(value: float) -> str:
    """Map value to rich color string: blue <5, green <20, yellow <50, red."""
    if value >= 50:
        return "red"
    elif value >= 20:
        return "yellow"
    elif value >= 5:
        return "green"
    return "blue"