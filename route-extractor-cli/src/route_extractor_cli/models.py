from typing import List, Optional
from pydantic import BaseModel


class Parameter(BaseModel):
    name: str
    type_hint: Optional[str] = None
    required: bool = True


class Route(BaseModel):
    methods: List[str]
    path: str
    handler: str
    parameters: List[Parameter] = []
    summary: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "methods": ["GET"],
                "path": "/users/{user_id}",
                "handler": "app.read_user",
                "parameters": [{"name": "user_id", "type_hint": "int", "required": True}],
            }
        }


Route.model_rebuild()
