import tokenize
import io
from typing import List, Tuple
from pathlib import Path

TokenPos = Tuple[str, int]

IGNORED_TYPES = {
    tokenize.COMMENT,
    tokenize.STRING,
    tokenize.ENCODING,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
}


def tokenize_file(path: Path) -> Tuple[List[TokenPos], List[str]]:
    """
    Tokenize Python file into normalized tokens with line positions, skipping ignorables.

    Returns (norm_tokens, lines) where norm_tokens is list of (normalized_str, start_line).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        lines = source.splitlines(keepends=True)
    except UnicodeDecodeError:
        # Gracefully skip non-UTF8
        return [], []

    norm_tokens: List[TokenPos] = []
    g = tokenize.tokenize(io.StringIO(source).readline)
    for tok in g:
        if tok.type in IGNORED_TYPES:
            continue

        ttype, tstr, start, *_ = tok
        sline = start[0]

        # Normalize
        if ttype == tokenize.NAME:
            norm_str = "ID"
        elif ttype == tokenize.NUMBER:
            norm_str = "NUM"
        elif ttype == tokenize.OP:
            norm_str = tstr
        else:
            norm_str = tokenize.tok_name[ttype]

        norm_tokens.append((norm_str, sline))

    return norm_tokens, lines


def tokenize_source(source: str) -> Tuple[List[TokenPos], List[str]]:
    """
    Tokenize source string (for tests).
    """
    lines = source.splitlines(keepends=True)
    norm_tokens: List[TokenPos] = []
    g = tokenize.tokenize(io.StringIO(source).readline)
    for tok in g:
        if tok.type in IGNORED_TYPES:
            continue
        ttype, tstr, start, *_ = tok
        sline = start[0]
        if ttype == tokenize.NAME:
            norm_str = "ID"
        elif ttype == tokenize.NUMBER:
            norm_str = "NUM"
        elif ttype == tokenize.OP:
            norm_str = tstr
        else:
            norm_str = tokenize.tok_name[ttype]
        norm_tokens.append((norm_str, sline))
    return norm_tokens, lines
