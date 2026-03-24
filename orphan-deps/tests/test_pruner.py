import textwrap
from pathlib import Path

import pytest
from orphan_deps.pruner import perform_prune


def test_prune_dry_run(sample_project: Path):
    reqs = sample_project / "requirements.txt"
    removed = perform_prune(sample_project, reqs, dry_run=True)
    assert 'unused-pkg' in textwrap.dedent(reqs.read_text())
    assert len(removed) >= 1


def test_prune_real(sample_project: Path):
    reqs = sample_project / "requirements.txt"
    orig_content = reqs.read_text()
    try:
        perform_prune(sample_project, reqs, dry_run=False)
        new_content = reqs.read_text()
        assert 'unused-pkg' not in new_content
        backup = reqs.with_suffix('.orphan-deps-backup')
        assert backup.exists()
        assert orig_content == backup.read_text()
    finally:
        reqs.write_text(orig_content)
        (reqs.with_suffix('.orphan-deps-backup')).unlink(missing_ok=True)