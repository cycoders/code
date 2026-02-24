from typing import List, Dict, Any, Set
from collections import defaultdict, Counter
import re

def infer_schema_from_samples(samples: List[Any], threshold: float = 0.8) -> Dict[str, Any]:
    """Infer JSON Schema from multiple samples (recursive, majority vote)."""
    if not samples:
        return {"type": "null"}

    sample_types = [get_type(v) for v in samples]
    type_counts = Counter(sample_types)
    majority_type = type_counts.most_common(1)[0][0]

    if majority_type == "object":
        return _infer_object_schema(samples, threshold)
    elif majority_type == "array":
        items = []
        all_items = [item for s in samples if isinstance(s, list) for item in s]
        if all_items:
            items.append(infer_schema_from_samples(all_items[:50], threshold))  # sample
        return {"type": "array", "items": {"oneOf": items} if items else {"type": "object"}}
    elif majority_type == "string":
        formats = _infer_string_formats(samples)
        return {"type": "string", **formats}
    elif majority_type == "number":
        return {"type": "number" if any(isinstance(s, float) for s in samples) else "integer"}
    elif majority_type == "boolean":
        return {"type": "boolean"}
    else:
        return {"type": ["null", "string"]}


def _infer_object_schema(samples: List[Any], threshold: float) -> Dict[str, Any]:
    all_keys: Set[str] = set()
    for s in samples:
        if isinstance(s, dict):
            all_keys.update(s.keys())

    properties = {}
    required = []
    key_samples = defaultdict(list)
    for s in samples:
        if isinstance(s, dict):
            for k in all_keys:
                if k in s:
                    key_samples[k].append(s[k])

    for key, vals in key_samples.items():
        prop_schema = infer_schema_from_samples(vals, threshold)
        properties[key] = prop_schema
        if len(vals) >= len(samples) * threshold:
            required.append(key)

    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _infer_string_formats(samples: List[Any]) -> Dict[str, Any]:
    str_samples = [s for s in samples if isinstance(s, str)]
    if not str_samples:
        return {}

    patterns = {
        "uuid": sum(1 for s in str_samples if re.match(r'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$', s.lower())),
        "email": sum(1 for s in str_samples if re.match(r'^[^@]+@[^@]+\.[^@]+$', s)),
        "date-time": sum(1 for s in str_samples if re.match(r'^\d{4}-\d{2}-\d{2}', s)),
    }
    max_count = max(patterns.values())
    if max_count / len(str_samples) > 0.8:
        for fmt, count in patterns.items():
            if count == max_count:
                return {"format": fmt}
    return {}


def get_type(value: Any) -> str:
    if value is None:
        return "null"
    t = type(value).__name__
    return "integer" if t == "int" else "number" if t == "float" else t
