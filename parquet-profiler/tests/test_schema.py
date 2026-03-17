def test_schema_info(sample_parquet):
    from parquet_profiler.schema import get_schema
    schema = get_schema(str(sample_parquet))
    assert schema.num_columns == 3
    assert all("name" in f for f in schema.fields)

# Edge: empty parquet

def test_empty_parquet(tmp_path):
    import pyarrow as pa
import pyarrow.parquet as pq
    empty_table = pa.table({})
    pq.write_table(empty_table, tmp_path / "empty.parquet")
    from parquet_profiler.schema import get_schema
    schema = get_schema(str(tmp_path / "empty.parquet"))
    assert schema.num_columns == 0
    assert schema.num_rows == 0
