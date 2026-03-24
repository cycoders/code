import ast
import re
from pathlib import Path
from typing import Set, Iterator

import tomllib
from packaging.requirements import Requirement, InvalidRequirement

from .types import PackageName

STDLIB_MODULES: Set[PackageName] = {
    # Core
    'os', 'sys', 'io', 'builtins',
    # Time/Data
    'time', 'datetime', 'calendar', 'zoneinfo',
    # Math/Random
    'math', 'random', 'statistics', 'decimal', 'fractions',
    # Text/Data
    'json', 'csv', 're', 'pathlib', 'string', 'textwrap', 'unicodedata',
    # Typing/Collections
    'typing', 'collections', 'itertools', 'functools', 'operator',
    'heapq', 'bisect', 'enum', 'dataclasses',
    # Context/Files
    'contextlib', 'tempfile', 'shutil', 'glob', 'fnmatch',
    # Logging/Config
    'logging', 'argparse', 'configparser',
    # Processes
    'subprocess', 'threading', 'multiprocessing', 'asyncio',
    'concurrent', 'signal', 'weakref',
    # Utils
    'copy', 'pickle', 'struct', 'uuid',
    # Crypto/Compress
    'base64', 'hashlib', 'hmac', 'secrets', 'zlib', 'gzip', 'bz2', 'lzma',
    'zipfile', 'tarfile',
    # Network
    'ssl', 'socket', 'http', 'urllib', 'email',
    # Misc
    'xml', 'html', 'sqlite3', 'inspect', 'traceback', 'pdb',
    'cProfile', 'timeit', 'difflib',
}


def is_excluded_pyfile(py_file: Path) -> bool:
    rel_parts = py_file.relative_to(py_file.parent.parent).parts  # root-aware
    skip_dirs = {'__pycache__', '.git', 'venv', '.venv', 'dist', 'build', '.tox', 'node_modules'}
    return any(skip_dir in rel_parts for skip_dir in skip_dirs)


def collect_top_level_imports(root: Path) -> Set[PackageName]:
    """Collect lowercase top-level module names from import statements, excl. stdlib."""
    used: Set[PackageName] = set()
    for py_file in root.rglob('*.py'):
        if not py_file.is_file() or py_file.name.startswith('.') or is_excluded_pyfile(py_file):
            continue
        try:
            tree = ast.parse(py_file.read_text(errors='ignore'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_level = alias.name.partition('.')[0].lower()
                        if top_level not in STDLIB_MODULES:
                            used.add(top_level)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    top_level = node.module.partition('.')[0].lower()
                    if top_level not in STDLIB_MODULES:
                        used.add(top_level)
        except (SyntaxError, UnicodeDecodeError):
            pass  # Skip invalid files
    return used


def parse_requirements_file(file_path: Path) -> Set[PackageName]:
    """Parse requirements.txt, extract lowercase package names."""
    pkgs: Set[PackageName] = set()
    try:
        for line in file_path.read_text().splitlines():
            line = line.split('#')[0].strip()
            if line:
                try:
                    req = Requirement(line)
                    pkgs.add(req.name.lower())
                except InvalidRequirement:
                    pass
    except Exception:
        pass
    return pkgs


def parse_pyproject(file_path: Path) -> Set[PackageName]:
    """Parse pyproject.toml: Poetry deps + [project.dependencies]."""
    pkgs: Set[PackageName] = set()
    try:
        data = tomllib.loads(file_path.read_text())
        # Poetry
        poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
        for pkg_name, _spec in poetry_deps.items():
            if pkg_name.lower() != 'python':
                pkgs.add(pkg_name.lower())
        # PEP 621
        project_deps = data.get('project', {}).get('dependencies', [])
        for dep_str in project_deps:
            try:
                req = Requirement(dep_str)
                pkgs.add(req.name.lower())
            except InvalidRequirement:
                pass
    except Exception:
        pass
    return pkgs