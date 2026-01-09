import json
import os
from pathlib import Path
from typing import List
from ..models import LicenseInfo


def get_node_deps(root: Path) -> List[LicenseInfo]:
    lock_path = root / "package-lock.json"
    if not lock_path.exists():
        return []

    deps: List[LicenseInfo] = []
    try:
        with open(lock_path, "r") as f:
            lock_data = json.load(f)
        packages = lock_data.get("packages", {})
        root_deps = packages.get("", {}).get("dependencies", {})

        for dep_key, _ in root_deps.items():
            clean_name = dep_key.split("@")[0]
            pkg_info = None
            for pkg_path, info in packages.items():
                if pkg_path and pkg_path.split("/")[-1] == clean_name and pkg_path.startswith("node_modules/"):
                    pkg_info = info
                    break
            if pkg_info:
                license_ = pkg_info.get("license", "unknown")
                version = pkg_info.get("version", "unspecified")
                deps.append(LicenseInfo(name=clean_name, version=version, license=license_))
    except Exception:
        pass  # Graceful

    return deps
