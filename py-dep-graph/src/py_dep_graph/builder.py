import ast
from pathlib import Path
from typing import Dict

from rich.progress import Progress

from .finder import ImportFinder

from .graph import DepGraph


def find_python_files(root: Path) -> list[Path]:
    """Find all non-hidden .py files recursively."""
    return [p for p in root.rglob("*.py") if not p.name.startswith((".", "test", "tests"))]


def compute_module_name(root: Path, py_file: Path) -> str:
    """Compute dotted module name from path relative to root."""
    rel = py_file.relative_to(root).with_suffix("").as_posix()
    return rel.replace("/", ".")


def build_graph(root: Path = Path(".")) -> DepGraph:
    """Build dependency graph for Python project at root."""
    root = root.resolve()
    py_files = find_python_files(root)
    if not py_files:
        raise ValueError(f"No Python files found in {root}")

    local_modules: Dict[str, Path] = {
        compute_module_name(root, p): p for p in py_files
    }

    graph = DepGraph()

    with Progress() as progress:
        task = progress.add_task("[cyan]Parsing modules...", total=len(local_modules))
        for mod_name, path in local_modules.items():
            try:
                source = path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source, filename=str(path))
                finder = ImportFinder(mod_name)
                finder.visit(tree)
                for dep_name in finder.imported_modules:
                    if dep_name in local_modules:
                        graph.add_edge(mod_name, dep_name)
            except SyntaxError as e:
                progress.console.print(f"[yellow]Skipping {path.name}: {e}[/]", soft_wrap=True)
            progress.advance(task)

    return graph
