from dataclasses import dataclass

@dataclass
class Finding:
    file: str
    line: int
    query_count: int
    suggestion: str