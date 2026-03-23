import re
from typing import List, Dict, Any
from pydantic import BaseModel

from .models import Route


def parse_path_params(path: str) -> List[dict]:
    """Extract params from path templates."""
    params = []
    # FastAPI: /users/{user_id}, {user_id:int}
    for match in re.finditer(r"\{([^}:]+)(?::([^}]+))?\}", path):
        name = match.group(1)
        type_hint = match.group(2) or "str"
        params.append({"name": name, "type_hint": type_hint, "required": True})
    # Django: /users/<int:user_id>
    for match in re.finditer(r"<([a-z]+):([^>]+)>", path):
        type_hint, name = match.groups()
        params.append({"name": name, "type_hint": type_hint, "required": True})
    return params


def generate_openapi(routes: List[Route]) -> Dict[str, Any]:
    """Generate basic OpenAPI v3 spec."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Extracted API", "version": "1.0.0"},
        "paths": {},
    }
    for route in routes:
        path_key = route.path
        if path_key not in spec["paths"]:
            spec["paths"][path_key] = {}
        for method in route.methods:
            spec["paths"][path_key][method.lower()] = {
                "summary": route.summary or "",
                "parameters": [
                    {
                        "name": p.name,
                        "in": "path",
                        "required": p.required,
                        "schema": {"type": p.type_hint or "string"},
                    }
                    for p in route.parameters
                ],
                "responses": {"200": {"description": "OK"}},
            }
    return spec
