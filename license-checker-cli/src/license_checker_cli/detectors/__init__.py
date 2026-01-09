from typing import List
from pathlib import Path
from .python_detector import get_python_deps
from .node_detector import get_node_deps
from ..models import LicenseInfo


def detect_all_deps(root: Path) -> List[LicenseInfo]:
    return (
        get_python_deps(root)
        + get_node_deps(root)
    )