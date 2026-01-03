from typing import Optional, Dict, Any
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: Optional[str] = None
    refresh_token: Optional[str] = None


class JWTPayload(BaseModel):
    sub: str
    scope: Optional[str]
    iat: int
    exp: int
    iss: str
    aud: str


TokenDict = Dict[str, Any]
