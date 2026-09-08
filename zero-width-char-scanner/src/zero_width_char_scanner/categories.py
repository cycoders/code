from __future__ import annotations

INVISIBLE_CATEGORIES = {
    "zero_width": r"[\u200B-\u200D\uFEFF]",
    "bidi_override": r"[\u202A-\u202E\u2066-\u2069]",
    "soft_hyphen": r"\u00AD",
    "word_joiner": r"\u2060",
    "non_breaking": r"\u00A0",
    "object_replacement": r"\uFFFC",
}