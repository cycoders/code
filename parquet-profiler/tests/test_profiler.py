import pyarrow.dataset as ds
from parquet_profiler.profiler import profile_dataset
from parquet_profiler.schema import get_schema


def test_profile(sample_parquet):
    result = profile_dataset(str(sample_parquet))
    assert len(result.columns) == 3
    assert result.schema.num_rows == 5
    assert result.schema.num_columns == 3


def test_schema(sample_parquet):
    schema = get_schema(str(sample_parquet))
    assert schema.num_rows == 5
    assert "age" in [f["name"] for f in schema.fields]


def test_columns_filter(sample_parquet):
    result = profile_dataset(str(sample_parquet), columns=["salary"])
    assert len(result.columns) == 1
    assert result.columns[0].name == "salary"
