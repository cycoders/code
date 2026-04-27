import re
from datetime import datetime
from typing import List, Tuple
from .models import BlameBlock, BlameEntry

HEADER_FIELDS = [
    'commit',
    'author',
    'author-mail',
    'author-time',
    'author-tz',
    'committer',
    'committer-mail',
    'committer-time',
    'committer-tz',
    'filename',
]


def parse_blame_porcelain(porcelain: str) -> List[BlameEntry]:
    """Parse git blame --porcelain output into BlameEntries."""
    lines = porcelain.splitlines()
    i = 0
    entries: List[BlameEntry] = []
    lineno = 1

    while i < len(lines):
        if not lines[i].startswith('commit '):
            i += 1
            continue

        header = _parse_header(lines, i)
        i += len(HEADER_FIELDS)

        block_lines = []
        while i < len(lines) and lines[i].startswith(header['filename']):
            block_lines.append(lines[i])
            i += 1

        # Skip boundary if present
        if i < len(lines) and lines[i] == 'boundary':
            i += 1

        entries.extend(_block_to_entries(header, block_lines, lineno))
        lineno += len(block_lines)

    return entries


def _parse_header(lines: List[str], start: int) -> dict:
    header = {}
    for j, field in enumerate(HEADER_FIELDS):
        line = lines[start + j]
        if field == 'commit':
            header[field] = line[7:]
        elif field.endswith('-time'):
            ts, tz = line[12:].split(' ')
            header[field] = datetime.fromtimestamp(int(ts))
            header[field + '_tz'] = int(tz)
        elif field == 'filename':
            header[field] = line[9:]
        else:
            prefix_len = 7 if field.endswith('-mail') else len(field) + 1
            header[field] = line[prefix_len:]
    return header


def _block_to_entries(header: dict, block_lines: List[str], start_lineno: int) -> List[BlameEntry]:
    entries = []
    prev_commit = ""
    for idx, line in enumerate(block_lines):
        parts = re.split(r'\s+', line, maxsplit=3)
        if len(parts) >= 3:
            _, commit, prev, content = parts[0], parts[1], parts[2], ' '.join(parts[3:])
            prev_commit = prev
        else:
            content = line

        entries.append(BlameEntry(
            lineno=start_lineno + idx,
            commit=header['commit'],
            prev_commit=prev_commit,
            author=header['author'],
            author_time=header['author-time'],
            summary="",
            content=content.rstrip(),
        ))
    return entries
