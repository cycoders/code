from typing import TypedDict, Set

from pathlib import Path

PackageName = str


class AnalysisResult(TypedDict):
    used: Set[PackageName]
    declared: Set[PackageName]
    unused: Set[PackageName]