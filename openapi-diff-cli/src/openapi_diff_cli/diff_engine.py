import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class Change:
    location: str
    change_type: str  # 'added', 'removed', 'changed'
    impact: str  # 'breaking', 'non-breaking'
    description: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

OPERATION_METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'}

class OpenAPIDiffer:
    def __init__(self):
        self.changes: List[Change] = []

    def diff(self, old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> Dict[str, Any]:
        self._recursive_diff(old_spec, new_spec, "")
        summary = self._compute_summary()
        return {
            "summary": summary,
            "changes": [asdict(c) for c in self.changes],
        }

    def _recursive_diff(self, old: Any, new: Any, location: str) -> None:
        if old == new:
            return
        if old is None:
            impact, desc = self._classify(location, "added", new=new=new)
            self.changes.append(Change(location, "added", impact, desc, None, new))
            return
        if new is None:
            impact, desc = self._classify(location, "removed", old=old)
            self.changes.append(Change(location, "removed", impact, desc, old, None))
            return
        if isinstance(old, dict) and isinstance(new, dict):
            self._diff_dict(old, new, location)
        elif isinstance(old, list) and isinstance(new, list):
            self._diff_list(old, new, location)
        else:
            impact, desc = self._classify(location, "changed", old=old, new=new)
            self.changes.append(Change(location, "changed", impact, desc, old, new))

    def _diff_dict(self, old: Dict[str, Any], new: Dict[str, Any], location: str) -> None:
        all_keys = set(old) | set(new)
        for key in sorted(all_keys):  # Deterministic order
            child_loc = f"{location}.{key}" if location else key
            self._recursive_diff(old.get(key), new.get(key), child_loc)

    def _diff_list(self, old: List[Any], new: List[Any], location: str) -> None:
        max_len = max(len(old), len(new))
        for i in range(max_len):
            child_loc = f"{location}[{i}]"
            o = old[i] if i < len(old) else None
            n = new[i] if i < len(new) else None
            self._recursive_diff(o, n, child_loc)

    def _classify(
        self, location: str, change_type: str, old: Optional[Any] = None, new: Optional[Any] = None
    ) -> Tuple[str, str]:
        val = new if change_type == "added" else old
        desc = f"{change_type.capitalize()} at {location.split('.')[-1] if '.' in location else location}"

        # Paths
        if re.match(r'^paths\.[^\.]+$', location):
            if change_type == "added":
                return "non-breaking", "New API path added"
            return "breaking", "API path removed"

        # Operations
        if re.match(r'^paths\.[^\.]+\.(' + '|'.join(OPERATION_METHODS) + ')$', location):
            if change_type == "added":
                return "non-breaking", "New operation added"
            return "breaking", "Operation removed"

        # Parameters
        if '.parameters[' in location:
            param = val or {}
            required = param.get('required', False) if isinstance(param, dict) else False
            if change_type == "added":
                impact = "breaking" if required else "non-breaking"
                return impact, f"{'Required' if required else 'Optional'} parameter added"
            elif change_type == "removed":
                return "breaking", "Parameter removed"
            return "breaking", "Parameter changed"

        # Schema types
        if location.endswith('.type'):
            return "breaking", "Schema type changed"

        # Required
        if location.endswith('.required'):
            return "breaking", "Required property changed"

        # RequestBody
        if 'requestBody' in location:
            if change_type == "added":
                return "non-breaking", "New requestBody added"
            return "breaking", "requestBody changed/removed"

        # Responses
        if 'responses.' in location:
            if change_type == "added":
                return "non-breaking", "New response code added"
            return "breaking", "Response code removed/changed"

        # Components schemas
        if re.match(r'^components\.schemas\.[^\.]+$', location):
            if change_type == "added":
                return "non-breaking", "New schema added"
            return "breaking", "Schema removed"

        # Defaults
        impact = "non-breaking" if change_type in ("added", "changed") else "breaking"
        return impact, desc

    def _compute_summary(self) -> Dict[str, int]:
        breaking = sum(1 for c in self.changes if c.impact == "breaking")
        non_breaking = len(self.changes) - breaking
        return {
            "total_changes": len(self.changes),
            "breaking": breaking,
            "non_breaking": non_breaking,
        }

def compute_diff(old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> Dict[str, Any]:
    differ = OpenAPIDiffer()
    return differ.diff(old_spec, new_spec)
