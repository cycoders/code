from typing import List
from ariadne import ObjectType, Field
from ..rules import Issue


def check_deprecations(schema) -> List[Issue]:
    issues = []
    for type_name, type_def in schema.types.items():
        if isinstance(type_def, ObjectType):
            for field_name, field in type_def.fields.items():
                if getattr(field, "deprecated", False) and not getattr(field, "deprecation_reason", None):
                    issues.append(
                        {
                            "rule": "deprecated-no-reason",
                            "severity": "error",
                            "path": f"type {type_name}.{field_name}",
                            "message": "Deprecated field missing deprecationReason",
                            "fix": 'Add deprecationReason: "Use alternative"',
                        }
                    )
    return issues