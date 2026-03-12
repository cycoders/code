from typing import TypedDict, Dict, List, Any

class Dependency(TypedDict):
    ecosystem: str
    name: str
    version: str


class OSVVuln(TypedDict, total=False):
    id: str
    summary: str
    details: str
    severity: str
    affected: List[Dict[str, Any]]


class OSVAffected(TypedDict, total=False):
    package: Dict[str, str]
    ranges: List[Dict[str, Any]]