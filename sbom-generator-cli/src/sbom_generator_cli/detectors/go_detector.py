import subprocess
from pathlib import Path
from typing import List

from ..models import Component
from .detector import Detector


class GoDetector(Detector):
    MARKERS = ["go.mod"]

    def detect(self, path: Path) -> bool:
        return (path / "go.mod").exists()

    def collect(self, path: Path) -> List[Component]:
        result = subprocess.run(
            ["go", "list", "-m", "-f", "{{.Path}} {{.Version}}\n", "all"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Go list failed: {result.stderr.strip()}")
        lines = result.stdout.strip().splitlines()
        comps: List[Component] = []
        for line in lines:
            if line.strip():
                mod_path, version = line.rsplit(" ", 1)
                name = mod_path.split("/")[-1]
                purl = f"pkg:golang/{mod_path}@{version}"
                comps.append(Component(name=name, version=version, purl=purl))
        return comps
