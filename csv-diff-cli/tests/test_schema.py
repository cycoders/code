import pytest
from polars import DataFrame

from csv_diff_cli.schema import compare_schemas


@pytest.mark.parametrize("ignore", [[], ["salary"]])
def test_identical_schema(sample_df1, ignore):
    result = compare_schemas(sample_df1, sample_df1, set(ignore))
    assert result["only_in_1"] == []
    assert result["only_in_2"] == []
    assert result["dtype_mismatches"] == {}


def test_only_in_left(sample_df1):
    df2 = sample_df1.drop("salary")
    result = compare_schemas(sample_df1, df2, set())
    assert result["only_in_1"] == ["salary"]
    assert result["only_in_2"] == []


def test_dtype_mismatch(sample_df1):
    df2 = sample_df1.with_columns(pl.col("age").cast(pl.Float64))
    result = compare_schemas(sample_df1, df2, set())
    assert "age" in result["dtype_mismatches"]
    assert result["dtype_mismatches"]["age"][0].startswith("Int")
    assert result["dtype_mismatches"]["age"][1] == "Float64"