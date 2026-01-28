from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Parameter(BaseModel):
    """OpenAPI Parameter model."""
    name: str
    in_: str = Field(..., alias='in')
    schema: Dict[str, Any]


class Response(BaseModel):
    """OpenAPI Response model."""
    description: Optional[str] = None
    content: Dict[str, Dict[str, Any]]


class Operation(BaseModel):
    """OpenAPI Operation (method) model."""
    responses: Dict[str, Response]


class PathItem(BaseModel):
    """OpenAPI PathItem model."""
    get: Optional[Operation] = None
    post: Optional[Operation] = None
    put: Optional[Operation] = None
    delete: Optional[Operation] = None
    patch: Optional[Operation] = None


class OpenAPISpec(BaseModel):
    """Parsed OpenAPI 3.0 Spec."""
    openapi: str
    info: Dict[str, Any]
    paths: Dict[str, PathItem]