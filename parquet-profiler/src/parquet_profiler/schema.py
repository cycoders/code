import pyarrow.dataset as ds
from typing import Dict, Any
from .types import SchemaInfo

def get_schema(path: str) -> SchemaInfo:
    dataset = ds.dataset(path)
    fields = []
    for i, field in enumerate(dataset.schema):
        fields.append({
            "name": field.name,
            "type": str(field.type),
            "nullable": field.nullable,
            "num_children": field.num_children if hasattr(field, 'num_children') else 0,
        })
    return SchemaInfo(
        fields=fields,
        num_rows=dataset.count_rows(),
        num_columns=len(dataset.schema),
        total_size_bytes=None,  # TODO: compute from fragments
    )
