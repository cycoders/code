from typing import TypedDict, Dict, List, Any

from pathlib import Path


class PackageInfo(TypedDict):
    path: Path
    deps: Dict[str, List[str]]


DepsByName = Dict[str, List[PackageInfo]]


ConflictInfo = Dict[str, List[PackageInfo]]