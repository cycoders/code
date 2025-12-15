'''
Directory scanner using AST visitors.
'''

from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import ast
import fnmatch
import json

from rich.progress import Progress, SpinnerColumn, TextColumn

from pathspec import GitIgnoreSpec

from .visitor import EnvVarVisitor


def scan_directory(root: Path, exclude: List[str] = None) -> Dict:
    """
    Scan Python files for env vars.

    :param root: Project root
    :param exclude: Extra fnmatch patterns
    :return: {'vars': {var: {'type', 'locations'}}, 'summary': {...}}
    """
    root = root.resolve()
    exclude = exclude or []

    # Load .gitignore
    gitignore_path = root / '.gitignore'
    gitignore_patterns: List[str] = []
    if gitignore_path.is_file():
        gitignore_patterns = gitignore_path.read_text(
            encoding='utf-8', errors='ignore'
        ).splitlines()
    gitignore = GitIgnoreSpec.from_lines(gitignore_patterns)

    # Find .py files
    py_files = []
    for py_path in root.rglob('*.py'):
        rel_path = py_path.relative_to(root).as_posix()
        if (
            gitignore.match_file(rel_path)
            or any(fnmatch.fnmatch(rel_path, pat) for pat in exclude)
        ):
            continue
        py_files.append(py_path)

    vars_info: Dict = {
        'vars': {},
        'summary': {'total_files': len(py_files), 'total_vars': 0}
    }

    # Scan
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task('Scanning Python files...', total=len(py_files))
        for py_file in py_files:
            rel_path = py_file.relative_to(root).as_posix()
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source, filename=str(py_file))
                visitor = EnvVarVisitor(filename=rel_path)
                visitor.visit(tree)

                for var_name in visitor.vars:
                    if var_name not in vars_info['vars']:
                        vars_info['vars'][var_name] = {
                            'type': 'str',
                            'locations': [],
                            'default': None,
                        }
                    vars_info['vars'][var_name]['locations'].extend(visitor.locations[var_name])
                    if var_name in visitor.type_hints:
                        vars_info['vars'][var_name]['type'] = visitor.type_hints[var_name]

                progress.advance(task)
            except SyntaxError:
                console.print(f'[yellow]Skipping {rel_path}: syntax error[/]')
                continue

    # Dedup locations
    for var_info in vars_info['vars'].values():
        var_info['locations'] = list(set(var_info['locations']))

    vars_info['summary']['total_vars'] = len(vars_info['vars'])
    return vars_info