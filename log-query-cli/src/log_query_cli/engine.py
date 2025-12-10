import duckdb
import polars as pl

from typing import Union

QueryResult = Union[pl.DataFrame, pl.LazyFrame]


def run_query(df: pl.DataFrame, sql: str) -> pl.DataFrame:
    """
    Execute SQL query on DataFrame via DuckDB.

    Assumes 'logs' table.
    """
    con = duckdb.connect()
    try:
        con.register("logs", df)
        result = con.sql(sql).pl()
        return result
    except Exception as e:
        raise RuntimeError(f"SQL execution failed: {e}\nQuery: {sql}")
    finally:
        con.close()