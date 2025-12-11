'''curl-to-python: Convert curl commands to idiomatic Python requests/httpx code.'''

from .cli import app

__version__ = "0.1.0"
__all__ = ["app", "parse_curl", "parsed_to_code"]
