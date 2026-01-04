from __future__ import annotations
import json
from math import gcd
from typing import Any, Dict, List

from rich.json import JSON
import typer
from .stats import NodeStats, ValueStats


def infer_schema(samples: List[Any], confidence: float = 0.9) -> Dict[str, Any]:
    if not samples:
        return {"type": "null"}

    root_stats = NodeStats()
    for sample in samples:
        root_stats.update(sample)

    typer.echo(f"Analyzed {root_stats.sample_count} samples", err=True)
    return _build_schema(root_stats, confidence)


def _build_schema(stats: NodeStats, confidence: float) -> Dict[str, Any]:
    total = stats.sample_count
    struct_types = stats.structural_type
    max_struct, max_cnt = struct_types.most_common(1)[0]

    if max_cnt / total < 0.8:
        typer.echo(
            "Warning: Mixed top-level structures (>20% variance). Using majority.",
            err=True,
        )

    if max_struct == "object":
        return _build_object_schema(stats, confidence)
    if max_struct == "array":
        return _build_array_schema(stats, confidence)
    return _build_primitive_schema(stats)


def _build_object_schema(stats: NodeStats, confidence: float) -> Dict[str, Any]:
    schema: Dict[str, Any] = {"type": "object", "properties": {}}
    required: List[str] = []
    for name, prop_stats in sorted(stats.properties.items()):
        prop_schema = _build_schema(prop_stats, confidence)
        schema["properties"][name] = prop_schema
        if prop_stats.sample_count / stats.sample_count >= confidence:
            required.append(name)
    if required:
        schema["required"] = sorted(required)
    return schema


def _build_array_schema(stats: NodeStats, confidence: float) -> Dict[str, Any]:
    if stats.items_stats is None:
        return {"type": "array"}
    return {
        "type": "array",
        "items": _build_schema(stats.items_stats, confidence),
    }


def _build_primitive_schema(stats: NodeStats) -> Dict[str, Any]:
    if stats.value_stats is None:
        return {"type": "null"}

    vs: ValueStats = stats.value_stats
    total = sum(vs.type_counts.values())
    if total == 0:
        return {"type": "null"}

    primary_t, primary_ratio = vs.type_counts.most_common(1)[0]
    schema: Dict[str, Any] = {}

    if primary_ratio / total >= 0.8:
        schema["type"] = primary_t
    else:
        types_list = [t for t, c in vs.type_counts.items() if c / total >= 0.1]
        schema["type"] = sorted(types_list, key=lambda t: -vs.type_counts[t])

    # Nullable
    null_ratio = vs.type_counts["null"] / total
    if null_ratio > 0.05:
        current_type = schema["type"]
        if isinstance(current_type, str):
            schema["type"] = [current_type, "null"]
        else:
            if "null" not in current_type:
                current_type.append("null")

    _add_constraints(schema, vs)
    return schema


def _add_constraints(schema: Dict[str, Any], vs: ValueStats) -> None:
    # Enums / const for strings
    if "string" in schema.get("type", [] ) or schema.get("type") == "string":
        sv = vs.string_values
        if sv:
            unique = len(sv)
            top_cov = sum(c for _, c in sv.most_common(10)) / vs.type_counts["string"]
            if unique <= 10 and top_cov >= 0.9:
                schema["enum"] = sorted(sv, key=sv.get, reverse=True)

    # Const for booleans
    if "boolean" in schema.get("type", []) or schema.get("type") == "boolean":
        bool_total = vs.type_counts["boolean"]
        if vs.bool_true_count == bool_total:
            schema["const"] = True
        elif vs.bool_false_count == bool_total:
            schema["const"] = False

    # Numbers
    if vs.number_values:
        nums = vs.number_values
        unique_nums = set(nums)
        if len(unique_nums) <= 12:
            schema["enum"] = sorted(unique_nums)
        else:
            schema["minimum"] = min(nums)
            schema["maximum"] = max(nums)
            # multipleOf for integers
            if vs.integer_count == len(nums) and len(nums) > 1:
                g = int(nums[0])
                for n in nums[1:]:
                    g = gcd(g, int(n))
                if g > 1:
                    schema["multipleOf"] = g
