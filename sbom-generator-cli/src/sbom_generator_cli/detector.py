from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .models import Component, Detector as DetectorBase


class DetectorRegistry:
    """Registry of known detectors."""

    KNOWN_DETECTORS: List[type[DetectorBase]] = []  # Populated by subclasses

    def __init__(self, path: Path):
        self.path = path

    def get_active(self) -> List[DetectorBase]:
        """Get active detectors for path."""
        instances = [detector() for detector in self.KNOWN_DETECTORS]
        return [d for d in instances if d.detect(self.path)]


# Register detectors (monkeypatch for simplicity)
DetectorRegistry.KNOWN_DETECTORS = [
    PythonDetector,
    NpmDetector,
    CargoDetector,
    GoDetector,
]