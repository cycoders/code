from typing import List
from ariadne import Schema
from ..rules import Issue

MAX_DEPTH = 7


def check_perf(schema: Schema) -> List[Issue]:
    issues = []

    def max_depth(typ, visited=set()):
        if typ.name in visited:
            return 0
        visited.add(typ.name)
        depth = 0
        if hasattr(typ, 'fields'):
            for field in typ.fields.values():
                # Simplified: assume ObjectType fields add depth
                ftype = field.type
                depth = max(depth, 1 + max_depth(ftype, visited.copy()))
        return depth

    query_depth = max_depth(schema.query_type) if schema.query_type else 0
    if query_depth > MAX_DEPTH:
        issues.append(
            {
                "rule": "high-depth",
                "severity": "info",
                "path": "Query",
                "message": f"Potential max depth {query_depth} > {MAX_DEPTH}",
                "fix": "Flatten nested resolvers",
            }
        )

    return issues