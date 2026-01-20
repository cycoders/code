import pytest
import polars as pl
from csv_profiler.schema_inferrer import infer_schema


def test_infer_schema(sample_data):
    df = pl.DataFrame({
        "id": [1, 2],
        "name": ["a", None],
        "flag": [True, False],
    })
    sch = infer_schema(df)
    assert sch["properties"]["id"]["type"] == "integer"
    assert sch["properties"]["name"]["nullable"] is True
    assert sch["properties"]["flag"]["type"] == "boolean"