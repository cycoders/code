from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class Dialect(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class Strategy(str, Enum):
    ONLINE_BATCHED = "online-batched"
    TABLE_COPY = "table-copy"


class BackfillConfig(BaseModel):
    table: str = Field(..., min_length=1, description="Target table name")
    total_rows: int = Field(..., gt=0, description="Total rows to backfill")
    write_throughput_avg: float = Field(..., gt=0, description="Avg rows/second write speed")
    write_throughput_min: Optional[float] = Field(None, ge=0)
    write_throughput_max: Optional[float] = Field(None, ge=0)
    row_size_bytes: int = Field(1024, ge=1, description="Est. row size in bytes")
    strategy: Strategy = Field(Strategy.ONLINE_BATCHED, description="Migration strategy")
    dialect: Dialect = Field(Dialect.POSTGRESQL)
    max_batch_seconds: int = Field(60, gt=0, description="Max time per batch (s)")
    max_memory_mb: int = Field(4096, gt=0, description="Available memory (MB)")
    max_runtime_hours: Optional[float] = Field(None, gt=0)
    column: Optional[str] = Field(None, description="Column to update (if applicable)")
    where_clause: Optional[str] = None

    @validator("write_throughput_min", "write_throughput_max", pre=True, always=True)
    def validate_throughput_bounds(cls, v, values):
        avg = values.get("write_throughput_avg")
        if v is not None:
            if avg and (v < 0 or v > 10 * avg):
                raise ValueError("Throughput bounds should be reasonable relative to avg")
        return v

    @validator("row_size_bytes")
    def validate_row_size(cls, v):
        if v > 1_000_000:
            raise ValueError("Unrealistic row size >1MB")
        return v
