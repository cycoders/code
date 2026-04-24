from typing import List
from ariadne import Schema, ObjectType, InterfaceType, UnionType, EnumType, InputObjectType, ScalarType

from ..rules import Issue


def check_naming(schema: Schema) -> List[Issue]:
    issues: List[Issue] = []
    import re

    pascal = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
    camel = re.compile(r"^[a-z][a-zA-Z0-9]*$")

    for type_name, type_def in schema.types.items():
        # Type PascalCase
        if not pascal.match(type_name):
            issues.append(
                {
                    "rule": "type-pascal-case",
                    "severity": "error",
                    "path": f"type {type_name}",
                    "message": f"Type '{type_name}' must use PascalCase",
                    "fix": "Rename to PascalCase",
                }
            )

        # Fields camelCase
        if isinstance(type_def, (ObjectType, InterfaceType, InputObjectType)):
            for field_name in type_def.fields:
                if not camel.match(field_name):
                    issues.append(
                        {
                            "rule": "field-camel-case",
                            "severity": "warning",
                            "path": f"type {type_name}.{field_name}",
                            "message": f"Field '{field_name}' should use camelCase",
                            "fix": "Rename to camelCase",
                        }
                    )
    return issues