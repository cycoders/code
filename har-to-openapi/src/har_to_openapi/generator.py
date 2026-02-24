from typing import Dict, Any, DefaultDict, List
from collections import defaultdict
import re
from urllib.parse import parse_qs

from .inferrer import infer_schema_from_samples

EndpointData = Dict[str, Any]
Endpoints = Dict[str, Dict[str, EndpointData]]

_PARAM_PATTERNS = {
    r'^\d+$': '{id}',
    r'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$': '{uuid}',
    r'^[0-9a-f]{32,}$': '{hash}',
    r'^[a-z0-9_-]{21}$': '{key}',  # common API key len
}

def normalize_path(path: str) -> str:
    """Normalize path to template, e.g., /users/123 -> /users/{id}"."""
    segments = [s for s in path.strip('/').split('/') if s]
    norm_segs = []
    for seg in segments:
        normed = seg
        for pattern, replacement in _PARAM_PATTERNS.items():
            if re.match(pattern, seg, re.IGNORECASE):
                normed = replacement
                break
        norm_segs.append(normed)
    return '/' + '/'.join(norm_segs)

def group_endpoints(entries: List[Dict[str, Any]], min_samples: int = 2) -> Endpoints:
    """Group entries into endpoints by normalized path/method/host."""
    groups: DefaultDict[tuple, List[Dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        host = entry['host']
        path = normalize_path(entry['path'])
        method = entry['method']
        groups[(method, host, path)].append(entry)

    endpoints: Endpoints = defaultdict(dict)
    for (method, host, path), samples in groups.items():
        if len(samples) < min_samples:
            continue

        # Collect data
        req_bodies = [e['req_body'] for e in samples if e['req_body']]
        resp_groups = defaultdict(list)
        query_keys = set()
        times = []
        auth_schemes = Counter()

        for e in samples:
            query = parse_qs(e['query'])
            query_keys.update(query.keys())
            times.append(e['time'])
            auth = e['req_headers'].get('authorization')
            if auth:
                if auth.startswith('Bearer '):
                    auth_schemes['bearer'] += 1
                elif auth.startswith('Basic '):
                    auth_schemes['basic'] += 1

            resp_body = e['resp_body']
            if resp_body is not None:
                resp_groups[e['resp_status']].append(resp_body)

        endpoint_data = {
            'samples': len(samples),
            'req_schema': infer_schema_from_samples(req_bodies) if req_bodies else None,
            'query_params': list(query_keys),
            'responses': {str(status): infer_schema_from_samples(bodies) for status, bodies in resp_groups.items()},
            'avg_time': sum(times) / len(times) if times else 0,
            'auth': auth_schemes.most_common(1)[0][0] if auth_schemes else None,
        }
        endpoints[path][method] = endpoint_data

    return dict(endpoints)

def generate_openapi(endpoints: Endpoints) -> Dict[str, Any]:
    if not endpoints:
        raise ValueError("No endpoints found.")

    hosts = set(path.split('/')[0] for path in endpoints if path)
    host = next(iter(hosts), 'example.com')

    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "API inferred from HAR traffic",
            "version": "1.0.0",
            "description": f"Auto-generated from {len(endpoints)} endpoints.",
        },
        "servers": [{"url": f"https://{host}"}],
        "paths": {},
    }

    security_schemes = {}
    for path, ops in endpoints.items():
        path_obj: Dict[str, Any] = {}
        for method, data in ops.items():
            op = {
                "summary": f"{method.upper()} {path}",
                "parameters": [
                    {
                        "name": name,
                        "in": "query",
                        "schema": {"type": "string"},
                        "required": False,
                    }
                    for name in data["query_params"]
                ],
            }
            if data["req_schema"]:
                op["requestBody"] = {
                    "content": {
                        "application/json": {"schema": data["req_schema"]},
                    },
                }
            op["responses"] = {
                code: {
                    "description": f"{code}",
                    "content": {
                        "application/json": {"schema": schema},
                    },
                }
                for code, schema in data["responses"].items()
            }
            path_obj[method.lower()] = op

        spec["paths"][path] = path_obj

    # Auth
    if any(data.get('auth') for ops in endpoints.values() for data in ops.values()):
        spec["components"] = {"securitySchemes": {}}
        for path_ops in endpoints.values():
            for data in path_ops.values():
                auth_type = data.get('auth')
                if auth_type == 'bearer':
                    spec["components"]["securitySchemes"]["bearerAuth"] = {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                elif auth_type == 'basic':
                    spec["components"]["securitySchemes"]["basicAuth"] = {
                        "type": "http",
                        "scheme": "basic",
                    }

    return spec
