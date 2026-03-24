import pytest
from pathlib import Path

from orphan_deps.core import find_unused


def test_find_unused(sample_project: Path):
    stats = find_unused(sample_project)
    assert 'requests' in stats['used']
    assert 'flask' in stats['used']
    assert 'numpy' in stats['used']
    assert 'unused-pkg' in stats['unused']
    assert len(stats['unused']) >= 1