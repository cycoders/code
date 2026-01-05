from typing import List
from pydantic import BaseModel, EmailStr


class Address(BaseModel):
    street: str
    city: str


class User(BaseModel):
    name: str
    email: EmailStr
    age: int
    is_active: bool
    tags: List[str]
    address: Address
