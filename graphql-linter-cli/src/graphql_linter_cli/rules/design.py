from typing import List
from ariadne import Schema
from ..rules import Issue


def check_design(schema: Schema) -> List[Issue]:
    issues = []

    if not schema.query_type:
        issues.append(
            {
                "rule": "no-query-type",
                "severity": "error",
                "path": "schema",
                "message": "Schema must define a Query type",
                "fix": "type Query { ... }",
            }
        )

    # Enum missing description (example)
    for type_name, type_def in schema.types.items():
        if type_def.name.startswith("_"):  # Skip system
            continue
        if hasattr(type_def, 'description') and not type_def.description:
            issues.append(
                {
                    "rule": "enum-no-desc",
                    "severity": "warning",
                    "path": f"enum {type_name}",
                    "message": "Enums should have descriptions",
                    "fix": 'Add """Description"""',
                }
            )

    return issues