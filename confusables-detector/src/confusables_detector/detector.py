import confusables


def is_confusable(char: str) -> bool:
    """Check if a character is a confusable (skeleton != itself)."""
    if len(char) != 1:
        return False
    try:
        skel = get_skeleton(char)
        return skel != char
    except (KeyError, ValueError):
        return False


def get_skeleton(char: str) -> str:
    """Get the canonical skeleton for a character."""
    if len(char) != 1:
        raise ValueError("Single character expected")
    return confusables.skeleton(char)


def normalize(text: str) -> str:
    """Normalize text by replacing all confusables with canonical forms."""
    return confusables.normalize(text)
