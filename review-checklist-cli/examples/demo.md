# Sample Checklist

## HIGH (4 items)

### Run type checker

Check 2 Python files for type errors

**Run:** `mypy src/`

### Verify lockfile reproducibility

Test exact dep resolution

**Run:** `pip install -r requirements.txt --dry-run --report -`

## MEDIUM (3 items)

### Lint Python code

Enforce style & best practices

**Run:** `ruff check src/`