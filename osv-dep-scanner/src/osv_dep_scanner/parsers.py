import json
from pathlib import Path
import tomllib
from typing import List

from .types import Dependency


def detect_lockfile_type(path: Path) -> str:
    name = path.name
    text_snip = path.read_text()[:1024].lower()

    if name == "package-lock.json" and '"packages":' in text_snip:
        return "npm"
    elif name == "poetry.lock":
        return "pypi"
    elif name == "Cargo.lock" and "[[package]]" in text_snip:
        return "crates"
    else:
        raise ValueError(f"Unsupported lockfile: {path.name}")


def parse_lockfile(path: Path) -> List[Dependency]:
    lock_type = detect_lockfile_type(path)
    if lock_type == "npm":
        return _parse_npm(path)
    elif lock_type == "pypi":
        return _parse_poetry(path)
    elif lock_type == "crates":
        return _parse_cargo(path)
    raise ValueError(f"Unknown lock type: {lock_type}")


def _parse_npm(path: Path) -> List[Dependency]:
    data = json.loads(path.read_text())
    deps: List[Dependency] = []
    for pkg_path, info in data.get("packages", {}).items():
        if pkg_path == "":
            continue
        name = pkg_path.rstrip("/").split("/")[-1]
        version = info["version"]
        deps.append({"ecosystem": "npm", "name": name, "version": version})
    return deps


def _parse_poetry(path: Path) -> List[Dependency]:
    data = json.loads(path.read_text())
    deps: List[Dependency] = []
    for pkg in data.get("package", []):
        name = pkg["name"]
        version = pkg["version"]
        deps.append({"ecosystem": "PyPI", "name": name, "version": version})
    return deps


def _parse_cargo(path: Path) -> List[Dependency]:
    data = tomllib.loads(path.read_text())
    deps: List[Dependency] = []
    for pkg in data.get("package", []):
        name = pkg["name"]
        version = pkg["version"]
        deps.append({"ecosystem": "crates", "name": name, "version": version})
    return deps