from typing import Dict, List, NamedTuple, Tuple

from .models import ApiElement


class DiffResult(NamedTuple):
    removed: List[ApiElement]
    changed: List[Tuple[ApiElement, ApiElement]]
    added: List[ApiElement]


def diff(old_apis: set[ApiElement], new_apis: set[ApiElement]) -> DiffResult:
    """Compute API diff categories."""
    removed: List[ApiElement] = list(old_apis - new_apis)
    added: List[ApiElement] = list(new_apis - old_apis)

    changed: List[Tuple[ApiElement, ApiElement]] = []
    old_by_qualname: Dict[str, ApiElement] = {api.qualname: api for api in old_apis}
    new_by_qualname: Dict[str, ApiElement] = {api.qualname: api for api in new_apis}

    for qualname in old_by_qualname:
        if qualname in new_by_qualname:
            old_api = old_by_qualname[qualname]
            new_api = new_by_qualname[qualname]
            if old_api.kind == new_api.kind and old_api.arg_sigs != new_api.arg_sigs:
                changed.append((old_api, new_api))

    return DiffResult(removed, changed, added)