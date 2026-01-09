import importlib.metadata
import os
import re
import tomllib
from pathlib import Path
from typing import List, Optional
from ..models import LicenseInfo


def get_python_deps(root: Path) -> List[LicenseInfo]:
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        return []

    deps: List[LicenseInfo] = []
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # Poetry
        poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        for name, spec in poetry_deps.items():
            if name.lower() == "python":
                continue
            version = str(spec).split("^")[0] if isinstance(spec, str) else "unspecified"
            license_ = _get_package_license(name)
            deps.append(LicenseInfo(name=name, version=version, license=license_ or "unknown"))

        # PEP 621 / Hatch etc.
        project_deps = data.get("project", {}).get("dependencies", [])
        for req in project_deps:
            name = _parse_req_name(req)
            version = _parse_req_version(req)
            license_ = _get_package_license(name)
            deps.append(LicenseInfo(name=name, version=version, license=license_ or "unknown"))

    except Exception:
        pass  # Graceful

    return deps


def _parse_req_name(req: str) -> str:
    match = re.match(r"([^=><~!]+)[\s=><~!]*", req)
    return match.group(1).strip().strip("[]") if match else req


def _parse_req_version(req: str) -> str:
    match = re.search(r"[>=<~!]?=?([\d.]+)", req)
    return match.group(1) if match else "unspecified"


def _get_package_license(name: str) -> Optional[str]:
    try:
        norm_name = name.lower().replace("-", "_").replace("+", "_")
        dist = importlib.metadata.distribution(norm_name)
        md = dist.metadata
        license_text = md.get("License")
        if license_text:
            return license_text.strip()
        # Classifiers fallback
        classifiers = md.get_all("Classifier") or []
        for clf in classifiers:
            if clf.startswith("License :: OSI Approved :: "):
                return clf.split("::", 1)[1].strip()
        return None
    except importlib.metadata.PackageNotFoundError:
        return None
    except Exception:
        return None