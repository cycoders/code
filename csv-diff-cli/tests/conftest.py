import polars as pl
import pytest


@pytest.fixture
def sample_df1():
    return pl.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [30, 25, 28],
        "salary": [50000.0, 45000.0, None],
    })


@pytest.fixture
def sample_df2():
    return pl.DataFrame({
        "id": [1, 2, 4],
        "name": ["Alice", "Bobby", "David"],
        "age": [30, 26, 29],
        "salary": [50000.0, 46000.0, 47000.0],
    })