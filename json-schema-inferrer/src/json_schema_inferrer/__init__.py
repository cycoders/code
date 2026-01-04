__version__ = "0.1.0"

from .infer import infer_schema
from .cli import main

__all__ = ["infer_schema", "main"]
