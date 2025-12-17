import ast
import logging
from pathlib import Path
from typing import List

import typer

from .models import OverallStats, FileStats
from .visitor import CoverageVisitor

logger = logging.getLogger(__name__)


def find_python_files(root: Path, excludes: List[str]) -> list[Path]:
    """Yield Python files excluding patterns."""
    py_files = []
    for py_file in root.rglob("*.py"):
        rel_path = str(py_file.relative_to(root)).replace("\\", "/")
        if any(ex in rel_path for ex in excludes):
            continue
        py_files.append(py_file)
    return py_files


def analyze_directory(root: Path, excludes: List[str]) -> OverallStats:
    """Analyze all Python files in directory."""
    stats = OverallStats()
    py_files = find_python_files(root, excludes)

    for py_file in py_files:
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
            visitor = CoverageVisitor()
            visitor.visit(tree)
            file_stats = visitor.stats.to_file_stats(str(py_file.relative_to(root)))
            stats.merge(file_stats)
        except SyntaxError as e:
            typer.echo(f"[yellow]Skipping {py_file}: syntax error at line {e.lineno}[/yellow]")
        except Exception as e:
            logger.warning(f"Error analyzing {py_file}: {e}")

    return stats