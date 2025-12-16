import rapidfuzz
from pathlib import Path
from typing import List, Tuple

from .blocks import extract_blocks
from .models import CodeBlock, Dupe
from .tokenizer import tokenize_file

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    "build",
    "dist",
    ".tox",
    "htmlcov",
    "site",
}


def detect_dupes(
    root: Path,
    min_tokens: int = 30,
    threshold: float = 0.85,
    step: int = 5,
    max_results: int = 20,
) -> List[Dupe]:
    """
    Detect duplicate code blocks in the project.
    """
    blocks = []
    pyfiles = list(root.rglob("*.py"))

    for pyfile in pyfiles:
        if any(ign in pyfile.parts for ign in IGNORED_DIRS):
            continue
        try:
            norm_tokens, lines = tokenize_file(pyfile)
            if len(norm_tokens) < min_tokens:
                continue
            blocks.extend(
                extract_blocks(pyfile, norm_tokens, lines, min_tokens, step)
            )
        except Exception:
            continue  # Gracefully skip unparseable files

    # Limit blocks for perf (rarely hit)
    if len(blocks) > 2000:
        blocks = blocks[:2000]

    dupes = _find_similar_pairs(blocks, threshold)
    dupes.sort(key=lambda x: x[0], reverse=True)
    return dupes[:max_results]


def _find_similar_pairs(blocks: List[CodeBlock], threshold: float) -> List[Dupe]:
    dupes: List[Dupe] = []
    n = len(blocks)
    for i in range(n):
        for j in range(i + 1, n):
            sim = (
                rapidfuzz.fuzz.token_sort_ratio(
                    blocks[i].token_str, blocks[j].token_str
                )
                / 100.0
            )
            if sim >= threshold:
                dupes.append((sim, blocks[i], blocks[j]))
    return dupes
