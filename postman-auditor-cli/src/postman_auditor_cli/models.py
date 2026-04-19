from typing import List, Optional, Union, Any, Dict, ForwardRef
from pydantic import BaseModel, Field, ConfigDict, ValidationError


class Variable(BaseModel):
    key: str
    value: Optional[str] = None


class Header(BaseModel):
    key: str
    value: str


class Body(BaseModel):
    mode: str
    raw: Optional[str] = None


class Url(BaseModel):
    raw: str


class Request(BaseModel):
    method: str
    header: Optional[List[Header]] = None
    body: Optional[Body] = None
    url: Url


ItemRef = ForwardRef('Item')

class Item(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: Optional[str] = None
    request: Optional[Request] = None
    item: Optional[List[ItemRef]] = None
    variable: Optional[List[Variable]] = None
    auth: Optional[Dict[str, Any]] = None


class Collection(BaseModel):
    info: Dict[str, Any]
    variable: Optional[List[Variable]] = None
    auth: Optional[Dict[str, Any]] = None
    item: List[Item]


# Rebuild forward refs
Item.model_rebuild()


__all__ = ["Collection", "Item", "Request", "Variable", "Header", "Body", "Url"]
