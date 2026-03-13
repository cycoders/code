import tomlkit
from collections import Counter
from packaging.version import Version, InvalidVersion
from pathlib import Path

from .types import PackageInfo


def choose_aligned_spec(specs: list[str]) -> str:
    """
    Choose aligned spec: prefer max parsed version pinned, fallback to most common.
    """
    versions = []
    for spec in specs:
        # Extract version-like string (heuristic)
        vstr = (
            spec.strip()
            .rstrip("><=!~^ ")
            .split(",")[0]
            .strip("<>=")
        )
        try:
            versions.append(Version(vstr))
        except InvalidVersion:
            pass

    if versions:
        max_v = max(versions)
        return f"=={max_v}"

    # Fallback: most common spec
    return Counter(specs).most_common(1)[0][0]


def align_dep_in_package(
    pkg_path: Path, dep_name: str, new_spec: str, dry_run: bool = True
) -> bool:
    """
    Align dep in pyproject.toml, backup if applied.

    Returns True if updated.
    """
    try:
        with open(pkg_path, "r") as f:
            doc = tomlkit.parse(f.read())

        updated = False

        # PEP 621
        if "project" in doc and "dependencies" in doc["project"]:
            deps = doc["project"]["dependencies"]
            if dep_name in deps:
                deps[dep_name] = new_spec
                updated = True

        # Poetry
        if "tool" in doc and "poetry" in doc["tool"] and "dependencies" in doc["tool"]["poetry"]:
            poetry_deps = doc["tool"]["poetry"]["dependencies"]
            if dep_name in poetry_deps:
                info = poetry_deps[dep_name]
                if isinstance(info, dict) and "version" in info:
                    info["version"] = new_spec
                else:
                    poetry_deps[dep_name] = new_spec
                updated = True

        if updated and not dry_run:
            # Backup
            backup = pkg_path.with_suffix(".toml.bak")
            backup.write_text(pkg_path.read_text())
            # Write
            with open(pkg_path, "w") as f:
                f.write(tomlkit.dumps(doc))

        return updated

    except Exception:
        return False