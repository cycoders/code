import pytest
from high_entropy_string_scanner.scanner import shannon_entropy, scan_path

def test_entropy_empty():
    assert shannon_entropy('') == 0.0

def test_entropy_known():
    assert shannon_entropy('aaaa') < 1.0

def test_scan_filters_short():
    assert scan_path('tests/fixtures', 4.0) == []