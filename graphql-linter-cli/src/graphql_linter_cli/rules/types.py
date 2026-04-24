from typing import List, Dict, Any
from ariadne import Schema, ObjectType
from ..rules import Issue


def check_types(schema: Schema) -> List[Issue]:
    issues: List[Issue] = []

    # Empty object types
    for type_name, type_def in schema.types.items():
        if isinstance(type_def, ObjectType) and len(type_def.fields) == 0:
            issues.append(
                {
                    "rule": "empty-object-type",
                    "severity": "error",
                    "path": f"type {type_name}",
                    "message": "ObjectType must have at least one field",
                    "fix": "Add fields or use Scalar/Enum",
                }
            )

        # Duplicate fields (simplified, check field names unique)
        field_names = [f.name for f in type_def.fields.values()] if hasattr(type_def, 'fields') else []
        if len(field_names) != len(set(field_names)):
            dups = [name for name in set(field_names) if field_names.count(name) > 1]
            issues.append(
                {
                    "rule": "duplicate-field",
                    "severity": "error",
                    "path": f"type {type_name}",
                    "message": f"Duplicate fields: {', '.join(dups)}",
                    "fix": "Remove duplicates",
                }
            )

    return issues