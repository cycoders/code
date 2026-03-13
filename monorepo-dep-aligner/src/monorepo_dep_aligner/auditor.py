from collections import defaultdict, Counter
from typing import List, Dict

from .types import PackageInfo, ConflictInfo


def audit_deps(packages: List[PackageInfo]) -> ConflictInfo:
    """
    Audit packages for conflicting dep specs.

    Returns {dep_name: [usages]} where usages have conflicting specs.
    """
    all_deps: Dict[str, List[PackageInfo]] = defaultdict(list)

    for pkg in packages:
        for name, specs in pkg["deps"].items():
            all_deps[name].append(pkg)

    conflicts: ConflictInfo = {}
    for dep, usages in all_deps.items():
        all_specs = [spec for pkg in usages for spec in pkg["deps"].get(dep, [])]
        unique_specs = set(all_specs)
        if len(unique_specs) > 1:
            conflicts[dep] = usages

    return conflicts