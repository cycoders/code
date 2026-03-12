import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import requests
from packaging import version as ver
from rich.progress import track

from .parsers import parse_lockfile
from .types import Dependency, OSVVuln


_SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def scan_lockfile(path: Path) -> Dict[str, List[OSVVuln]]:
    deps = parse_lockfile(path)
    return _query_osv(deps)


def _query_osv(deps: List[Dependency]) -> Dict[str, List[OSVVuln]]:
    if not deps:
        return {}

    queries = [
        {
            "package": {"ecosystem": d["ecosystem"], "name": d["name"]},
            "version": d["version"],
        }
        for d in deps
    ]

    try:
        resp = requests.post(
            "https://api.osv.dev/v1/query",
            json={"version": queries},
            timeout=30,
            headers={"User-Agent": "osv-dep-scanner/0.1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to query OSV API: {e}") from e

    vulns = data["vulns"]
    vuln_by_dep: Dict[str, List[OSVVuln]] = defaultdict(list)

    for vuln in vulns:
        for aff in vuln.get("affected", []):
            pkg = aff["package"]
            ecos = pkg["ecosystem"]
            pname = pkg["name"]
            for d in deps:
                if d["ecosystem"] == ecos and d["name"] == pname:
                    if _is_version_affected(ver.parse(d["version"]), aff):
                        key = f"{ecos}/{d['name']}@{d['version']}"
                        vuln_by_dep[key].append(vuln)
    return dict(vuln_by_dep)


def _is_version_affected(dep_ver: ver.Version, affected: Dict) -> bool:
    ranges = affected.get("ranges", [])
    if not ranges:
        return True  # Assume affected if no range
    for rg in ranges:
        if rg["type"] != "SEMVER":
            continue
        events = rg[0].get("events", []) if rg else []
        if not events:
            continue
        # Common: events[0] introduced, events[1] fixed
        intro_ev = events[0]
        fixed_ev = events[1] if len(events) > 1 else None

        # Intro check
        if intro_ev.startswith("="):
            if dep_ver != ver.parse(intro_ev[1:]):
                continue
        elif intro_ev.startswith(">="):
            if dep_ver < ver.parse(intro_ev[2:]):
                continue
        # Fixed check
        if fixed_ev and fixed_ev.startswith("<"):
            if dep_ver >= ver.parse(fixed_ev[1:]):
                continue
        return True
    return False


def get_max_severity(vulns: List[OSVVuln]) -> str:
    return max((v.get("severity", "LOW") for v in vulns), key=lambda s: _SEVERITY_ORDER.get(s, 0))