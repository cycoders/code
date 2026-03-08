from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class Service(BaseModel):
    """Parsed Docker Compose service."""

    name: str
    image: Optional[str] = None
    build: Optional[Dict[str, Any]] = None
    ports: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    networks: List[str] = Field(default_factory=list)
    volumes: List[str] = Field(default_factory=list)
    healthcheck: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")

    @validator("ports", "depends_on", "networks", "volumes", pre=True)
    def parse_lists(cls, v):
        if isinstance(v, list):
            return [str(item) for item in v if item]
        return []


class Compose(BaseModel):
    """Full Docker Compose file model."""

    version: str = "3.8"
    services: Dict[str, Service] = Field(default_factory=dict)
    networks: Dict[str, Any] = Field(default_factory=dict)
    volumes: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow", populate_by_name=True)