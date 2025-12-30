__version__ = "0.1.0"

from .detector import is_confusable, get_skeleton, normalize

from .scanner import scan_directory

__all__ = [
    "is_confusable",
    "get_skeleton",
    "normalize",
    "scan_directory",
]