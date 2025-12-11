import pytest
from pii_anonymizer.anonymizer import Anonymizer
from pii_anonymizer.types import AnonymizeMode


@pytest.mark.parametrize("mode", ["fake", "hash", "redact"])
def test_anonymizer_modes(sample_df):
    series = sample_df["email"]
    mask = pd.Series([True, True], index=series.index)
    ptypes = pd.Series(["email", "email"], index=series.index)

    anonymizer = Anonymizer(AnonymizeMode(mode))
    result = anonymizer.anonymize_series(series, mask, ptypes)

    assert not (result == series).all()  # Changed
    if mode == "redact":
        assert (result == "***********").all()
