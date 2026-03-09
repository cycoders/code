import json
import tomllib
from pathlib import Path
from typing import Dict, Optional, Tuple

def parse_npm_lock(lock_path: Path) -> Tuple[Dict[str, str], Optional[int], Dict[str, int]]:
    """Parse npm package-lock.json."""
    with lock_path.open("r", encoding="utf-8") as f:
        lock_data = json.load(f)

    deps: Dict[str, str] = {}
    sizes: Dict[str, int] = {}
    total_size = 0

    packages = lock_data.get("packages", {})
    for pkg_data in packages.values():
        if isinstance(pkg_data, dict):
            name = pkg_data.get("name")
            version = pkg_data.get("version")
            if name and version:
                deps[name] = version
                unpacked_size = pkg_data.get("unpackedSize")
                if isinstance(unpacked_size, int):
                    sizes[name] = unpacked_size
                    total_size += unpacked_size

    return deps, total_size, sizes

def parse_poetry_lock(lock_path: Path) -> Tuple[Dict[str, str], Optional[int], Optional[Dict[str, int]]]:
    """Parse Poetry poetry.lock."""
    with lock_path.open("rb") as f:
        lock_data = tomllib.load(f)

    deps: Dict[str, str] = {}
    packages = lock_data.get("package", [])
    for pkg in packages:
        if isinstance(pkg, dict):
            name = pkg.get("name")
            version = pkg.get("version")
            if name and version:
                deps[name] = version

    return deps, None, None

def parse_cargo_lock(lock_path: Path) -> Tuple[Dict[str, str], Optional[int], Optional[Dict[str, int]]]:
    """Parse Cargo Cargo.lock."""
    with lock_path.open("rb") as f:
        lock_data = tomllib.load(f)

    deps: Dict[str, str] = {}
    packages = lock_data.get("package", [])
    for pkg in packages:
        if isinstance(pkg, dict):
            name = pkg.get("name")
            version = pkg.get("version")
            if name and version:
                deps[name] = version

    return deps, None, None
