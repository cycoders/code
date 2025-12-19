import math
import re
from typing import Optional


def shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy of a string in bits per character."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = [0] * 256
    for char in data:
        counts[ord(char)] += 1
    for count in counts:
        if count > 0:
            p_x = count / length
            entropy -= p_x * math.log2(p_x)
    return entropy


def mask_snippet(snippet: str) -> str:
    """Mask potential secrets in snippet for safe display."""
    # Mask long hex-like
    snippet = re.sub(r'[a-fA-F0-9]{12,}', lambda m: m.group(0)[:6] + '***' + m.group(0)[-6:], snippet)
    # Mask base64-like
    snippet = re.sub(r'[A-Za-z0-9+/]{20,}', lambda m: m.group(0)[:10] + '***' + m.group(0)[-10:], snippet)
    # Truncate
    if len(snippet) > 100:
        snippet = snippet[:97] + '...'
    return snippet