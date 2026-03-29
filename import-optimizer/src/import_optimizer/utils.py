import libcst as cst
from pathlib import Path
from typing import Iterable, List

from pathspec import PathSpec
from rich.console import Console

console = Console()


def find_python_files(
    root: Path, recursive: bool = True, gitignore: bool = True
) -> Iterable[Path]:
    """
    Yield Python files respecting .gitignore.
    """
    if isinstance(root, str):
        root = Path(root)

    spec: PathSpec | None = None
    gitignore_path = root / ".gitignore"
    if gitignore and gitignore_path.is_file():
        spec = PathSpec.from_lines("gitwildmatch", gitignore_path.read_text().splitlines())

    pattern = "**/*.py" if recursive else "*.py"
    for py_file in root.glob(pattern):
        if spec is None or py_file.relative_to(root) not in spec:
            yield py_file