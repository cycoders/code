from pydantic import ValidationError
from .models import ServiceConfig

def validate_config(data: dict) -> ServiceConfig:
    try:
        return ServiceConfig(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid config: {e}") from e