from typing import Any, Dict, List
from ariadne import Schema

Issue = Dict[str, Any]

RULE_DETAILS = {
    "type-pascal-case": {"short": "type-pascal-case", "desc": "Types must use PascalCase"},
    "field-camel-case": {"short": "field-camel-case", "desc": "Fields must use camelCase"},
    "deprecated-no-reason": {"short": "deprecated-no-reason", "desc": "Deprecated fields need reason"},
    "empty-object-type": {"short": "empty-type", "desc": "Object types must have fields"},
    "duplicate-field": {"short": "dup-field", "desc": "Duplicate fields in type"},
    "no-query-type": {"short": "no-query", "desc": "Schema must define Query"},
    "enum-no-desc": {"short": "enum-no-desc", "desc": "Enums need descriptions"},
    "list-no-max": {"short": "list-no-max", "desc": "Lists should have max size arg"},
    "high-depth": {"short": "high-depth", "desc": "High nesting depth"},
}

__all__ = ["RULE_DETAILS"]