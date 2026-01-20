import pytest
import polars as pl
from pathlib import Path
from csv_profiler.profiler import profile_csv

@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    content = """id,name,age,salary,city,is_active
1,Alice,30,50000.0,New York,true
2,Bob,,60000.0,Los Angeles,false
3,Alice,30,50000.0,New York,true
4,Carol,25,45000.0,Chicago,true
5,David,35,,New York,false
"""
    p = tmp_path / "sample.csv"
    p.write_text(content)
    return p

@pytest.fixture
def sample_data() -> dict:
    return profile_csv(Path("tests/data/sample.csv"))