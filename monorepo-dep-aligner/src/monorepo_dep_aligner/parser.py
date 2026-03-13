import tomllib
from pathlib import Path
from typing import Dict, List, Optional, Any


def find_pyprojects(root: Path) -> List[Path]:
    """Find all pyproject.toml files recursively."""
    return list(root.rglob("pyproject.toml"))


def parse_package_deps(path: Path) -> Optional[Dict[str, List[str]]]:
    """
    Parse runtime dependencies from pyproject.toml.

    Supports:
    - [project.dependencies] (PEP 621)
    - [tool.poetry.dependencies] (Poetry)

    Returns {dep_name: [spec_strs]} or None if no deps/no valid file.
    """
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        deps: Dict[str, List[str]] = {}

        # PEP 621: [project.dependencies]
        proj = data.get("project", {})
        project_deps = proj.get("dependencies", {})
        for name, spec in project_deps.items():
            if isinstance(spec, str):
                deps.setdefault(name, []).append(spec)

        # Poetry: [tool.poetry.dependencies]
        tool = data.get("tool", {})
        poetry = tool.get("poetry", {})
        poetry_deps = poetry.get("dependencies", {})
        for name, info in poetry_deps.items():
            if name == "python":
                continue
            spec: str
            if isinstance(info, dict) and "version" in info:
                spec = info["version"]
            elif isinstance(info, str):
                spec = info
            else:
                continue
            deps.setdefault(name, []).append(spec)

        return deps if deps else None

    except (tomllib.TOMLDecodeError, OSError, KeyError):
        return None