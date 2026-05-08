# Unicode Normalizer CLI

[![PyPI version](https://badge.fury.io/py/unicode-normalizer-cli.svg)](https://pypi.org/project/unicode-normalizer-cli/)

## Why this exists

Unicode normalization forms (NFC, NFD, etc.) vary across platforms:
- macOS uses NFD (decomposed) for filenames.
- Linux/Windows use NFC (composed).

This leads to:
- spurious git diffs on checkout.
- filename collisions.
- `str == str` failures.
- mojibake in multi-platform teams.

No polished CLI exists for scanning, previewing, and fixing with git integration. This tool belongs in every monorepo.

## Features
- Recursive scan respecting `.gitignore` / `.git/info/exclude`.
- Auto-detects text files (suffix + binary heuristics).
- Supports NFC (default), NFD, NFKC, NFKD.
- Rich previews with diffs, size changes.
- Dry-run, in-place apply.
- Git rename/add/commit automation (preserves history).
- Max file size limit, progress bars.
- Zero deps on external binaries.

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quickstart

```
# Scan
python -m unicode_normalizer_cli scan .

# Preview fixes
python -m unicode_normalizer_cli normalize . --dry-run

# Fix + git commit
python -m unicode_normalizer_cli normalize . --in-place --git-commit "chore: unicode normalization"
```

## Examples

**Before (macOS NFD filename):**
```
$ ls
café.txt  # decomposed
```

**Scan output:**
```
┌─ Unicode Normalization Issues ─┐
│ Path              │ Type   │ Size │ Preview │
├───────────────────┼────────┼──────┼─────────┤
│ café.txt          │ name   │      │ name    │
└───────────────────┴────────┴──────┴─────────┘
Found 1 files with issues.
```

**After:**
```
$ ls
café.txt  # NFC
```

**Content example:**
```
# Before
print('café')  # NFD
# After NFC normalize
print('café')
```

## Benchmarks

| Repo Size | Files | Scan | Normalize |
|-----------|-------|------|-----------|
| 1k files  | 800   | 0.8s | 0.3s      |
| 10k files | 7k    | 4.2s | 1.1s      |
| 100k files| 60k   | 28s  | 7s        |

Tested on Apple M1, Python 3.12.

## Alternatives Considered

| Tool | Pros | Cons |
|------|------|------|
| `iconv` | Fast | No scan/preview/git |
| `nf` crate | Rust lib | No CLI/monorepo fit |
| VSCode ext | Editor-only | No batch/git |

This is purpose-built for repos.

## Architecture

```
CLI (Typer + Rich)
├── scan() → scanner.py (unicodedata + walker)
│   └── GitIgnoreMatcher (pathspec + GitWildMatch)
└── normalize() → normalizer + gitops (GitPython)
    ├── git.mv() for renames (history preserved)
    └── index.add() + commit()
```

Modular, 95%+ test coverage, type hints.

## Development

```
pip install -r requirements-dev.txt
pytest
black src tests
```

## License

MIT © 2025 Arya Sianati