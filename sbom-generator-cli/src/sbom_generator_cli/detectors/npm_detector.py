import json
import subprocess
from pathlib import Path
from typing import List

from ..models import Component
from .detector import Detector


class NpmDetector(Detector):
    MARKERS = ["package.json", "package-lock.json", "yarn.lock"]

    def detect(self, path: Path) -> bool:
        return any((path / marker).exists() for marker in self.MARKERS)

    def collect(self, path: Path) -> List[Component]:
        # Use npm ls even for yarn.lock (consistent format)
        result = subprocess.run(
            ["npm", "ls", "--all", "--json"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode not in (0, 1):  # 1 ok if unmet peers
            raise RuntimeError(f"NPM ls failed: {result.stderr.strip()}")
        data = json.loads(result.stdout)
        comps: List[Component] = []

        def flatten_deps(obj: dict):
            if "dependencies" in obj:
                for name, info in obj["dependencies"].items():
                    version = info.get("version", "unknown")
                    purl = f"pkg:npm/{name}@{version}"
                    comps.append(Component(name=name, version=version, purl=purl))
                    flatten_deps(info)

        flatten_deps(data)
        return comps
