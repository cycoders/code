import pytest
from copyleft_risk_analyzer.scanner import scan

def test_empty_scan():
    assert 'markdown' in scan()