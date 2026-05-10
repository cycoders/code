from __future__ import annotations

from pathlib import Path
import re
from collections.abc import Iterable

from pathspec import GitIgnoreSpec

from .config import Config

from .types import Usage


def get_default_gitignore_lines() -> list[str]:
    return [
        ".git/",
        "node_modules/",
        "dist/",
        "build/",
        ".next/",
        "out/",
        "venv/",
        "__pycache__/",
        "*.pyc",
    ]


def scan_directory(root: Path, config: Config) -> list[Usage]:
    """Scan directory for feature flag usages."""

    # Load gitignore spec
    gitignore_lines = get_default_gitignore_lines()
    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_lines = f.readlines()
    spec = GitIgnoreSpec.from_lines(".gitignore", gitignore_lines)

    usages: list[Usage] = []

    for pattern in config.patterns:
        try:
            compiled_re = re.compile(pattern.regex, re.MULTILINE | re.DOTALL)
        except re.error as e:
            print(f"Invalid regex '{pattern.name}': {e}")
            continue

        target_langs = pattern.langs or config.exts.keys()
        for lang in target_langs:
            if lang not in config.exts:
                continue
            for glob_pattern in config.exts[lang]:
                for file_path in root.rglob(glob_pattern):
                    rel_path = file_path.relative_to(root).as_posix()
                    if spec.match_file(rel_path):
                        continue

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        for match in compiled_re.finditer(content):
                            start_pos = match.start()
                            line_no = content[:start_pos].count("\n") + 1
                            flag_name = match.group(pattern.capture_group) or ""
                            if flag_name:
                                snippet_start = max(0, start_pos - 30)
                                snippet_end = min(len(content), start_pos + len(flag_name) + 30)
                                snippet = (
                                    content[snippet_start:snippet_end]
                                    .replace("\n", " ")
                                    .strip()
                                )
                                usages.append(Usage(file_path, line_no, flag_name.strip(), snippet))
                    except (UnicodeDecodeError, OSError):
                        pass  # Skip binary/non-utf8

    return usages
