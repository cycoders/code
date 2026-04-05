from typing import Any, Dict, List

from .diff_model import DiffIssue, DiffIssues


def diff_schemas(
    schema1: Dict[str, Any],
    schema2: Dict[str, Any],
    path: str = "$",
) -> DiffIssues:
    """Recursively diff two JSON schemas, returning structured issues."""

    issues: DiffIssues = []

    # Handle $ref opaquely
    ref1 = schema1.get("$ref")
    ref2 = schema2.get("$ref")
    if ref1 is not None or ref2 is not None:
        if ref1 != ref2:
            issues.append(
                DiffIssue(
                    "ref_changed",
                    path,
                    description="Schema $ref changed",
                    old_value=ref1,
                    new_value=ref2,
                )
            )
        return issues

    if not (isinstance(schema1, dict) and isinstance(schema2, dict)):
        if type(schema1) != type(schema2):
            issues.append(
                DiffIssue(
                    "type_changed",
                    path,
                    description="Primitive type mismatch",
                    old_value=type(schema1).__name__,
                    new_value=type(schema2).__name__,
                )
            )
        elif schema1 != schema2:
            issues.append(
                DiffIssue(
                    "value_changed",
                    path,
                    description="Primitive value changed",
                    old_value=schema1,
                    new_value=schema2,
                )
            )
        return issues

    # Type
    t1 = schema1.get("type", "null")
    t2 = schema2.get("type", "null")
    if t1 != t2:
        issues.append(
            DiffIssue(
                "type_changed",
                path,
                f"Type changed from {t1} to {t2}",
                old_value=t1,
                new_value=t2,
            )
        )

    # Required
    req1: set[str] = set(schema1.get("required", []))
    req2: set[str] = set(schema2.get("required", []))
    for prop in req2 - req1:
        issues.append(
            DiffIssue(
                "required_added",
                f"{path}/required",
                f"New required field: {prop}",
                new_value=prop,
            )
        )
    for prop in req1 - req2:
        issues.append(
            DiffIssue(
                "required_removed",
                f"{path}/required",
                f"Removed required field: {prop}",
                old_value=prop,
            )
        )

    # Properties
    props1 = schema1.get("properties", {})
    props2 = schema2.get("properties", {})
    for prop, ps1 in props1.items():
        ppath = f"{path}/properties/{prop}"
        if prop not in props2:
            issues.append(
                DiffIssue(
                    "property_removed",
                    ppath,
                    "Property removed",
                    old_value=dict(ps1),
                )
            )
        else:
            issues.extend(diff_schemas(ps1, props2[prop], ppath))
    for prop in set(props2.keys()) - set(props1.keys()):
        ppath = f"{path}/properties/{prop}"
        issues.append(
            DiffIssue(
                "property_added",
                ppath,
                "New property added",
                new_value=dict(props2[prop]),
            )
        )

    # Enums
    enum1 = schema1.get("enum")
    enum2 = schema2.get("enum")
    if enum1 is not None or enum2 is not None:
        e1 = set(enum1 or [])
        e2 = set(enum2 or [])
        for v in e1 - e2:
            issues.append(
                DiffIssue("enum_removed", path, "Enum value removed", old_value=v)
            )
        for v in e2 - e1:
            issues.append(
                DiffIssue("enum_added", path, "Enum value added", new_value=v)
            )

    # Numeric/string constraints (tightening = potential break)
    constraints = [
        "minimum",
        "exclusiveMinimum",
        "minLength",
        "minProperties",
    ]
    for c in constraints:
        v1 = schema1.get(c)
        v2 = schema2.get(c)
        if v1 is not None and v2 is not None and v2 > v1:
            issues.append(
                DiffIssue(
                    "constraint_tightened",
                    f"{path}/{c}",
                    "Constraint tightened (potential break)",
                    old_value=v1,
                    new_value=v2,
                )
            )
    constraints_max = [
        "maximum",
        "exclusiveMaximum",
        "maxLength",
        "maxProperties",
    ]
    for c in constraints_max:
        v1 = schema1.get(c)
        v2 = schema2.get(c)
        if v1 is not None and v2 is not None and v2 < v1:
            issues.append(
                DiffIssue(
                    "constraint_tightened",
                    f"{path}/{c}",
                    "Constraint tightened (potential break)",
                    old_value=v1,
                    new_value=v2,
                )
            )

    # Array items
    if schema1.get("type") == "array" or schema2.get("type") == "array":
        items_path = f"{path}/items"
        i1 = schema1.get("items")
        i2 = schema2.get("items")
        if i1 is None and i2 is not None:
            issues.append(DiffIssue("items_added", items_path))
        elif i1 is not None and i2 is None:
            issues.append(DiffIssue("items_removed", items_path))
        elif i1 is not None and i2 is not None:
            issues.extend(diff_schemas(i1, i2, items_path))

    return issues