from typing import TypedDict, Dict, Any, List


class ResourceChange(TypedDict, total=False):
    address: str
    type: str
    name: str
    provider_name: str
    change: Dict[str, Any]


PlanDict = Dict[str, Any]
ChangesList = List[ResourceChange]