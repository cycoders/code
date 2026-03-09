from typing import Optional
from packaging.version import Version, InvalidVersion

def parse_version(version_str: str) -> Optional[Version]:
    """Parse a version string into packaging.Version."""
    try:
        return Version(version_str)
    except InvalidVersion:
        return None

def bump_type(old_ver: str, new_ver: str) -> str:
    """
    Classify semver bump type between two versions.

    Assumes both versions exist.
    """
    ov = parse_version(old_ver)
    nv = parse_version(new_ver)
    if ov is None or nv is None:
        return "unknown"

    if ov.major != nv.major:
        return "major"
    elif ov.minor != nv.minor:
        return "minor"
    elif ov.micro != nv.micro:
        return "patch"
    return "same"
