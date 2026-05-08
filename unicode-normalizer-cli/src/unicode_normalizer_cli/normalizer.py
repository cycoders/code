from typing import Tuple

import unicodedata


def needs_normalization(s: str, form: str = "NFC") -> Tuple[bool, str]:
    """
    Check if needs normalization.

    >>> needs_normalization('café', 'NFC')
    (False, 'café')
    >>> needs_normalization('caf\u0301e', 'NFC')
    (True, 'café')
    """
    norm = unicodedata.normalize(form, s)
    return norm != s, norm