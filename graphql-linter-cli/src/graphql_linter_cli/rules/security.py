from typing import List
from ariadne import Schema, ObjectType
from ..rules import Issue


def check_security(schema: Schema) -> List[Issue]:
    issues = []

    # Example: Mutations without 'auth' arg (heuristic)
    if schema.mutation_type:
        mut_fields = schema.mutation_type.fields
        risky = [f for f in mut_fields.values() if 'create' in f.name or 'delete' in f.name]
        for field in risky:
            if not any(arg.name == 'auth' for arg in getattr(field, 'args', [])):
                issues.append(
                    {
                        "rule": "public-mutation-without-auth",
                        "severity": "warning",
                        "path": f"Mutation.{field.name}",
                        "message": "Potentially public mutation lacks auth arg",
                        "fix": "Add auth: String! arg",
                    }
                )

    return issues