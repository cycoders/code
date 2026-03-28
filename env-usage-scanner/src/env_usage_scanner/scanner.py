import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set, Optional

from rich.progress import Progress
from rich.progress import SpinnerColumn, TextColumn

import env_usage_scanner.models as models
import env_usage_scanner.parsers as parsers


EXT_TO_LANG = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'javascript',
    '.go': 'go',
    '.sh': 'shell',
    '.bash': 'shell',
    '.env': None,  # Skip
    '.yml': None,
    '.yaml': None,
}

COMPOSE_FILENAMES = {
    'docker-compose.yml',
    'docker-compose.yaml',
    'compose.yml',
    'compose.yaml',
    'docker-compose.override.yml',
}

DEFAULT_EXCLUDES = {
    'node_modules', 'venv', 'env', '.git', '__pycache__', 'dist', 'build', '.next', 'target',
}


def get_language(path: Path) -> str | None:
    """Map file extension/name to language."""
    name = path.name
    ext = path.suffix.lower()

    if name == 'Dockerfile':
        return 'dockerfile'
    if name in COMPOSE_FILENAMES:
        return 'compose'

    lang = EXT_TO_LANG.get(ext)
    if lang:
        return lang
    return None


def scan_directory(
    root: Path,
    include_langs: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
) -> models.UsageMap:
    """Scan directory recursively for env usages."""

    exclude_paths = exclude_paths or []
    usages_map: models.UsageMap = defaultdict(list)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Scanning files...", total=None)

        for path in root.rglob("*"):
            if path.is_dir():
                if any(ex in path.name for ex in DEFAULT_EXCLUDES | set(exclude_paths)):
                    progress.update(task, description=f"Skipping {path.name}")
                    path.glob("**/*")  # Skip traversal
                    continue
                continue

            if not path.is_file():
                continue

            lang = get_language(path)
            if not lang:
                continue
            if include_langs and lang not in include_langs:
                continue

            progress.update(task, description=f"Parsing {path.name}")
            file_usages = parsers.parse_file(path, lang)
            for usage in file_usages:
                usages_map[usage.var_name].append(usage)

    return dict(usages_map)


def parse_env_file(env_path: Path) -> Set[str]:
    """Parse defined vars from .env file."""
    defined = set()
    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                var = line.split('=', 1)[0].strip()
                if re.match(r'^[A-Z_][A-Z0-9_]*$', var):
                    defined.add(var)
    except Exception:
        pass
    return defined
