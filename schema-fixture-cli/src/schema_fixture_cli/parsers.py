import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import importlib.util
import typer
from pydantic import BaseModel


def get_schema_dict(
    schema_file: Path,
    pydantic_module: Optional[Path],
    pydantic_model: str,
    component: Optional[str],
) -> Dict[str, Any]:
    if pydantic_module:
        if not pydantic_model:
            raise typer.BadParameter("--model required with --pydantic-module")
        return load_pydantic_schema(pydantic_module, pydantic_model)
    return load_file_schema(schema_file, component)


def load_pydantic_schema(module_path: Path, model_name: str) -> Dict[str, Any]:
    spec = importlib.util.spec_from_file_location("temp_module", module_path)
    if spec is None:
        raise ValueError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    if not hasattr(module, model_name):
        raise ValueError(f"Model '{model_name}' not found in {module_path}")
    model_cls = getattr(module, model_name)
    if not issubclass(model_cls, BaseModel):
        raise ValueError(f"'{model_name}' is not a Pydantic BaseModel")
    return model_cls.model_json_schema()


def load_file_schema(file_path: Path, component: Optional[str]) -> Dict[str, Any]:
    content = file_path.read_text(encoding="utf-8")
    if file_path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)

    if is_openapi(data):
        return extract_openapi_component(data, component)
    return data


def is_openapi(data: Dict[str, Any]) -> bool:
    return "openapi" in data or "swagger" in data


def extract_openapi_component(data: Dict[str, Any], component: Optional[str]) -> Dict[str, Any]:
    components = data.get("components", {}).get("schemas", {})
    if not components:
        raise ValueError("No 'components.schemas' found in OpenAPI spec")

    if component is None:
        raise typer.BadParameter(
            f"OpenAPI spec detected. Specify --component (available: {list(components.keys())} )"
        )

    if component not in components:
        avail = ", ".join(sorted(components.keys())[:10])
        raise ValueError(
            f"Component '{component}' not found. Available: {avail}{'...' if len(components) > 10 else ''}"
        )
    return components[component]
