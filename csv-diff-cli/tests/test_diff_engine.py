import pytest
from polars import DataFrame

from csv_diff_cli.diff_engine import compute_key_hash, detect_changes


def test_key_hash_no_keys(sample_df1):
    df_keyed = compute_key_hash(sample_df1, [])
    assert df_keyed["key_hash"].to_list() == [0, 1, 2]


def test_key_hash_with_keys(sample_df1):
    df_keyed = compute_key_hash(sample_df1, ["id", "name"])
    assert df_keyed["key_hash"].to_list() == ["1|Alice", "2|Bob", "3|Charlie"]


@pytest.mark.parametrize("tol", [0.0, 1000.0])
def test_detect_changes(sample_df1, sample_df2, tol):
    df1_keyed = compute_key_hash(sample_df1.with_row_index(), ["id"])
    df2_keyed = compute_key_hash(sample_df2.with_row_index(), ["id"])
    merged = df1_keyed.join(df2_keyed, on="key_hash", how="full", suffix="_right")
    changes = detect_changes(merged, {"name", "age", "salary"}, tol)
    assert len(changes) == (2 if tol == 0.0 else 1)