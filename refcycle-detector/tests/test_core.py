import pytest
from refcycle_detector.core import CycleDetector

def test_detects_simple_cycle():
    d = CycleDetector()
    assert d.scan() == []