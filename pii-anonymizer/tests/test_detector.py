import pytest
import pandas as pd
import re

from pii_anonymizer.detector import Detector
from pii_anonymizer.patterns import COMPILED_PATTERNS


@pytest.mark.parametrize("text,pattern_name,expected", [
    ("john@example.com", "email", True),
    ("(555) 123-4567", "phone_us", True),
    ("123-45-6789", "ssn_us", True),
    ("not_pii", "email", False),
])
def test_pattern_matching(text, pattern_name, expected):
    pattern = COMPILED_PATTERNS[pattern_name]
    assert bool(pattern.search(text)) == expected


def test_detect_column_stats(sample_df):
    detector = Detector(threshold=0.0)
    stats = detector.detect_column_stats(sample_df)

    pii_cols = {s.column for s in stats}
    assert pii_cols.issuperset({"email", "phone", "ssn_us", "address"})
    assert len(stats) >= 4


def test_get_pii_mask_and_type(sample_df):
    detector = Detector()
    mask, ptype = detector.get_pii_mask_and_type(sample_df["email"])
    assert mask.all()
    assert (ptype == "email").all()
