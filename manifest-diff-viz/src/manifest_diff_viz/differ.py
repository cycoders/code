import json
from typing import Dict, List, Any, Tuple
from .parser import get_resource_key

DEFAULT_IGNORES = [
    'status',
    'metadata.creationTimestamp',
    'metadata.resourceVersion',
    'metadata.uid',
    'metadata.generation',
    'metadata.managedFields',
    'metadata.finalizers',
]

ResourceMap = Dict[str, Dict[str, Any]]
ResourceDiffs = Dict[str, List[Dict[str, Any]]]

 def compute_resource_diffs(
    before_docs: List[Dict[str, Any]],
    after_docs: List[Dict[str, Any]],
    ignores: List[str],
) -> ResourceDiffs:
    """Compute diffs grouped by resource key."""
    before_map = _docs_to_map(before_docs)
    after_map = _docs_to_map(after_docs)
    all_keys = set(before_map) | set(after_map)
    diffs: ResourceDiffs = {}
    for key in sorted(all_keys):
        before_res = before_map.get(key)
        after_res = after_map.get(key)
        if before_res is None:
            diffs[key] = [{'type': 'added', 'path': [], 'value': after_res}]
        elif after_res is None:
            diffs[key] = [{'type': 'removed', 'path': [], 'value': before_res}]
        else:
            res_diff = compute_diff(before_res, after_res, ignores)
            if res_diff:
                diffs[key] = res_diff
    return diffs

def _docs_to_map(docs: List[Dict[str, Any]]) -> ResourceMap:
    return {get_resource_key(doc): doc for doc in docs}

def compute_diff(
    old: Dict[str, Any], new: Dict[str, Any], ignores: List[str], path: List[str] = []
) -> List[Dict[str, Any]]:
    """Recursive dict diff. Returns list of changes."""
    if should_ignore(path, ignores):
        return []
    changes: List[Dict[str, Any]] = []
    all_keys = set(old.keys()) | set(new.keys())
    for k in sorted(all_keys):
        p = path + [k]
        old_val = old.get(k)
        new_val = new.get(k)
        if k not in old:
            changes.append({'type': 'added', 'path': p, 'value': new_val})
        elif k not in new:
            changes.append({'type': 'removed', 'path': p, 'value': old_val})
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            sub_changes = compute_diff(old_val, new_val, ignores, p)
            changes.extend(sub_changes)
        else:
            # Serialize non-dicts for comparison (handles lists/prim)
            old_ser = json.dumps(old_val, sort_keys=True) if old_val is not None else None
            new_ser = json.dumps(new_val, sort_keys=True) if new_val is not None else None
            if old_ser != new_ser:
                changes.append({
                    'type': 'modified',
                    'path': p,
                    'old': old_val,
                    'new': new_val
                })
    return changes

def should_ignore(path: List[str], ignores: List[str]) -> bool:
    """Check if path matches any ignore rule."""
    pstr = '.'.join(path)
    return any(ign == pstr or pstr.startswith(ign) for ing in ignores)