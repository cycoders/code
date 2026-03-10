from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Submodule:
    """Dataclass representing a parsed Git submodule."""
    path: str
    url: str
    current_commit: str
    target_branch: str | None
    is_dirty: bool
    outdated: bool
    days_behind: int
    issues: List[str]


def submodules_to_dict(subs: List[Submodule]) -> List[dict]:
    """Convert list of Submodule to serializable dicts."""
    return [asdict(sub) for sub in subs]
