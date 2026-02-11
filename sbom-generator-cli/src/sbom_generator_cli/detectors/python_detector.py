import json
import subprocess
from pathlib import Path
from typing import List

from ..models import Component
from .detector import Detector


class PythonDetector(Detector):
    MARKERS = ["pyproject.toml", "poetry.lock", "requirements.txt", "Pipfile"]

    def detect(self, path: Path) -> bool:
        return any((path / marker).exists() for marker in self.MARKERS)

    def collect(self, path: Path) -> List[Component]:
        comps: List[Component] = []
        if (path / "poetry.lock").exists():
            comps.extend(self._parse_poetry(path))
        if (path / "requirements.txt").exists():
            comps.extend(self._parse_pip(path))
        return comps

    def _parse_poetry(self, path: Path) -> List[Component]:
        result = subprocess.run(
            ["poetry", "show", "--no-dev", "-f", "json"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Poetry failed: {result.stderr.strip()}")
        pkgs = json.loads(result.stdout)
        return [
            Component(
                name=pkg["name"],
                version=pkg["version"],
                purl=f"pkg:pypi/{pkg['name']}@{pkg['version']}",
            )
            for pkg in pkgs
        ]

    def _parse_pip(self, path: Path) -> List[Component]:
        result = subprocess.run(
            ["pip", "list", "--format", "json"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Pip list failed: {result.stderr.strip()}")
        pkgs = json.loads(result.stdout)
        return [
            Component(
                name=pkg["name"],
                version=pkg["version"],
                purl=f"pkg:pypi/{pkg['name']}@{pkg['version']}",
            )
            for pkg in pkgs if pkg["version"] != "(path)"  # Skip editable
        ]
