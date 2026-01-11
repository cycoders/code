import json
from pathlib import Path
import tomlkit
from typing import Dict, List, Tuple

def parse_graph(
    parser_type: str,
    project_path: Path,
    lock_path: Path,
    manifest_path: Optional[Path],
    include_dev: bool,
) -> Tuple[List[str], Dict[str, List[str]]]:
    if parser_type == "poetry":
        return _parse_poetry(lock_path, manifest_path)
    elif parser_type == "npm":
        return _parse_npm(lock_path, manifest_path, include_dev)
    elif parser_type == "cargo":
        return _parse_cargo(lock_path, manifest_path, include_dev)
    raise ValueError(f"Unknown parser: {parser_type}")

def _parse_poetry(lock_path: Path, manifest_path: Optional[Path]) -> Tuple[List[str], Dict[str, List[str]]]:
    lock_doc = tomlkit.parse(lock_path.read_text())
    packages = lock_doc["package"]

    pkg_name_to_nv: Dict[str, str] = {}
    graph: Dict[str, List[str]] = {}

    for pkg in packages:
        name: str = pkg["name"]
        ver: str = pkg["version"]
        nv = f"{name}@{ver}"
        pkg_name_to_nv[name] = nv

        deps = pkg.get("dependencies", [])
        dep_names = []
        for dep in deps:
            if isinstance(dep, dict) and len(dep) == 1:
                dep_name = next(iter(dep))
                if dep_name != "python":
                    dep_names.append(dep_name)
        graph[nv] = [pkg_name_to_nv.get(dn, dn) for dn in dep_names]

    roots = []
    if manifest_path and manifest_path.exists():
        proj_doc = tomlkit.parse(manifest_path.read_text())
        deps = proj_doc.get("tool", {}).get("poetry", {}).get("dependencies", {})
        for name in deps:
            if name != "python" and name in pkg_name_to_nv:
                roots.append(pkg_name_to_nv[name])
    else:
        # Fallback: packages with no incoming (simple indegree)
        all_deps = set(nv for nvs in graph.values() for nv in nvs)
        roots = [nv for nv in graph if nv not in all_deps]

    return roots, graph

def _parse_npm(lock_path: Path, manifest_path: Optional[Path], include_dev: bool) -> Tuple[List[str], Dict[str, List[str]]]:
    lock_data: dict = json.loads(lock_path.read_text())
    packages = lock_data.get("packages", {})

    graph: Dict[str, List[str]] = {}

    for pkg_path, info in packages.items():
        if "name" not in info or "version" not in info:
            continue
        nv = f"{info['name']}@{info['version']}"
        graph[nv] = []
        if "dependencies" in info:
            for sub_path in info["dependencies"].values():
                if sub_path in packages:
                    sub_info = packages[sub_path]
                    sub_nv = f"{sub_info['name']}@{sub_info['version']}"
                    graph[nv].append(sub_nv)

    roots = []
    if manifest_path and manifest_path.exists():
        pkg_data = json.loads(manifest_path.read_text())
        dep_types = ["dependencies"] + (["devDependencies"] if include_dev else [])
        for dep_type in dep_types:
            if dep_type in pkg_data:
                for name in pkg_data[dep_type]:
                    for candidate_nv in list(graph):
                        if candidate_nv.startswith(name + "@"):
                            roots.append(candidate_nv)
                            break
    else:
        root_info = packages.get("")
        if root_info:
            roots = [f"{root_info['name']}@{root_info['version']}"]

    return roots, graph

def _parse_cargo(lock_path: Path, manifest_path: Optional[Path], include_dev: bool) -> Tuple[List[str], Dict[str, List[str]]]:
    lock_doc = tomlkit.parse(lock_path.read_text())
    packages = lock_doc["package"]

    pkg_name_to_nv: Dict[str, str] = {}
    graph: Dict[str, List[str]] = {}

    for pkg in packages:
        name: str = pkg["name"]
        ver: str = pkg["version"]
        nv = f"{name}@{ver}"
        pkg_name_to_nv[name] = nv

        deps = pkg["dependencies"]
        dep_names = []
        for dep in deps:
            if isinstance(dep, str):
                dep_name = dep.split()[0].split(" ")[0]
            elif isinstance(dep, dict):
                dep_name = next(iter(dep))
            else:
                continue
            if dep_name and dep_name != "rustc-std-workspace-core":
                dep_names.append(dep_name)
        graph[nv] = [pkg_name_to_nv.get(dn, dn) for dn in dep_names]

    roots = []
    if manifest_path and manifest_path.exists():
        toml_doc = tomlkit.parse(manifest_path.read_text())
        dep_secs = ["dependencies"] + (["dev-dependencies"] if include_dev else [])
        for sec in dep_secs:
            deps = toml_doc.get(sec, {})
            for name in deps:
                if name in pkg_name_to_nv:
                    roots.append(pkg_name_to_nv[name])
    else:
        all_deps = set(nv for nvs in graph.values() for nv in nvs)
        roots = [nv for nv in graph if nv not in all_deps]

    return roots, graph