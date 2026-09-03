from dataclasses import dataclass

@dataclass
class Column:
    name: str
    dtype: str
    constraints: dict

class SchemaParser:
    """Parses JSON Schema / DDL into internal Column model."""
    def parse(self, source: str):
        return []