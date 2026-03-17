import pytest
import pyarrow as pa
import pyarrow.parquet as pq
import tempfile
import os
from pathlib import Path

@pytest.fixture
def sample_parquet(tmp_path: Path):
    table = pa.table({
        "age": [25, 30, None, 45, 22],
        "name": ["Alice", "Bob", "Charlie", None, "Alice"],
        "salary": [50000.0, 60000.0, 70000.0, None, 55000.0],
    })
    path = tmp_path / "test.parquet"
    pq.write_table(table, path)
    return path

@pytest.fixture
def large_sample_parquet(tmp_path: Path):
    # Larger for progress test
    data = {k: list(range(10000)) + [None] * 1000 for k in ["int_col", "float_col"]}
    data["str_col"] = ["x"] * 5000 + ["y"] * 5000 + [None] * 1000
    table = pa.table(data)
    path = tmp_path / "large.parquet"
    pq.write_table(table, path)
    return path
