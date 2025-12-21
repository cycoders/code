import fnmatch
from pathlib import Path
from typing import Set, Dict, List

import ast
import networkx as nx
from rich.progress import Progress

from .visitors import ImportVisitor


def discover_modules(root: Path, exclude: List[str]) -> Set[str]:
    """
    Discover all Python modules under root, handling __init__.py -> parent module.
    """
    modules: Set[str] = set()
    exclude_patterns = exclude

    for py_path in root.rglob("*.py"):
        rel = py_path.relative_to(root)
        # Skip excluded
        if any(fnmatch.fnmatch(part, pat) for part in rel.parts for pat in exclude_patterns):
            continue
        if py_path.read_bytes().startswith(b"#!"):  # Skip shebangs? Nah
            pass

        if py_path.name == "__init__.py":
            mod_path = rel.parent
        else:
            mod_path = rel
        module = mod_path.with_suffix("").as_posix().replace("/", ".")
        modules.add(module)

    return modules


def get_file_path(root: Path, module: str) -> Path:
    """
    Resolve file path for a module name (prefers __init__.py).
    """
    path = root / Path(module.replace(".", "/"))
    init_path = path / "__init__.py"
    if init_path.exists():
        return init_path
    return path.with_suffix(".py")


def build_graph(root: Path, exclude: List[str]) -> nx.DiGraph:
    """
    Build import dependency DiGraph: edge A -> B if A statically imports local B.
    """
    exclude_set = set(exclude)
    all_modules = discover_modules(root, exclude)

    G = nx.DiGraph()
    G.add_nodes_from(all_modules)

    with Progress() as progress:
        task = progress.add_task("[cyan]Parsing modules...", total=len(all_modules))
        for module_name in sorted(all_modules):
            file_path = get_file_path(root, module_name)
            if not file_path.exists():
                progress.advance(task)
                continue
            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(file_path))
                visitor = ImportVisitor(module_name)
                visitor.visit(tree)
                for imp_mod in visitor.imported_modules:
                    if imp_mod in all_modules:
                        G.add_edge(module_name, imp_mod)
            except (SyntaxError, UnicodeDecodeError):
                pass  # Skip broken files
            progress.advance(task)

    return G