import ast
import logging
import os
from pathlib import Path
from typing import List

from .models import ClassInfo

from .visitors import ASTClassVisitor


logger = logging.getLogger(__name__)


class FileParser:
    """Parses a single Python file for classes."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.module_name = filepath.stem

    def parse(self) -> List[ClassInfo]:
        """Parse file and return list of ClassInfo."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(self.filepath))
            visitor = ASTClassVisitor(module_name=self.module_name)
            visitor.visit(tree)
            return visitor.classes
        except SyntaxError as e:
            logger.warning(f"Syntax error in {self.filepath}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse {self.filepath}: {e}")
            return []


class CodebaseCollector:
    """Collects ClassInfo from entire codebase."""

    def __init__(self, root: Path, exclude: List[str] = None):
        self.root = root
        self.exclude = exclude or []
        self.classes: List[ClassInfo] = []

    def collect(self) -> List[ClassInfo]:
        """Walk directory and collect all classes."""
        pyfiles = [
            p
            for p in self.root.rglob("*.py")
            if p.is_file() and not self._should_exclude(p)
        ]
        for pyfile in pyfiles:
            parser = FileParser(pyfile)
            self.classes.extend(parser.parse())
        return self.classes

    def _should_exclude(self, path: Path) -> bool:
        return any(fnmatch.fnmatch(path.name, excl) for excl in self.exclude)
