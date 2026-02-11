import json
import subprocess
from pathlib import Path
from typing import List

from ..models import Component
from .detector import Detector


class CargoDetector(Detector):
    MARKERS = ["Cargo.toml", "Cargo.lock"]

    def detect(self, path: Path) -> bool:
        return any((path / marker).exists() for marker in self.MARKERS)

    def collect(self, path: Path) -> List[Component]:
        result = subprocess.run(
            ["cargo", "metadata", "--format-version=1"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Cargo metadata failed: {result.stderr.strip()}")
        data = json.loads(result.stdout)
        packages = data["packages"]
        comps: List[Component] = []
        for pkg in packages:
            pkg_id = pkg["id"]
            if pkg_id.startswith("virtual/"):
                continue  # Skip workspace members
            comps.append(
                Component(
                    name=pkg["name"],
                    version=pkg["version"],
                    purl=pkg_id,
                )
            )
        return comps
