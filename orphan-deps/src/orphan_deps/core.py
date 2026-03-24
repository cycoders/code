from pathlib import Path
from typing import Optional

from .parsers import collect_top_level_imports, parse_requirements_file, parse_pyproject

from .types import AnalysisResult, PackageName


def find_unused(
    root: Path,
    req_file: Optional[Path] = None,
    use_poetry: bool = False,
) -> AnalysisResult:
    """Analyze project: return used/declared/unused sets."""
    used = collect_top_level_imports(root)
    declared: set[PackageName] = set()

    if req_file:
        declared = parse_requirements_file(req_file)
    elif use_poetry:
        pyproj = root / 'pyproject.toml'
        if pyproj.exists():
            declared = parse_pyproject(pyproj)
    else:
        # Auto-detect
        req_files = list(root.glob('requirements*.txt')) + list(root.glob('req*.txt'))
        if req_files:
            declared = parse_requirements_file(req_files[0])
        pyproj = root / 'pyproject.toml'
        if pyproj.exists():
            declared |= parse_pyproject(pyproj)

    unused = declared - used
    return {'used': used, 'declared': declared, 'unused': unused}