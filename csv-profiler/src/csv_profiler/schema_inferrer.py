from typing import Dict, Any, List
from polars import DataFrame

DtypeMap = {
    "Boolean": "boolean",
    "Int8": "integer",
    "Int16": "integer",
    "Int32": "integer",
    "Int64": "integer",
    "UInt8": "integer",
    "UInt16": "integer",
    "UInt32": "integer",
    "UInt64": "integer",
    "Float32": "number",
    "Float64": "number",
    "String": "string",
    "Date": "string",  # format: date
    "Datetime": "string",  # format: date-time
}


def infer_schema(df: DataFrame) -> Dict[str, Any]:
    """Infer JSON Schema-like structure."""
    properties = {}
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        type_ = DtypeMap.get(dtype_str, "string")
        nullable = df[col].null_count() > 0
        enums = None
        if df[col].n_unique() <= 10:
            enums = df[col].unique().to_list()
        properties[col] = {
            "type": type_,
            "nullable": nullable,
            "enum": enums,
        }
    return {"type": "object", "properties": properties}