import pytest
from blast_radius_cli.core import compute_blast_radius

def test_basic_radius():
    r = compute_blast_radius("HEAD~1", "HEAD")
    assert r["radius"] >= 0

def test_deterministic():
    a = compute_blast_radius("main", "feature")
    b = compute_blast_radius("main", "feature")
    assert a == b