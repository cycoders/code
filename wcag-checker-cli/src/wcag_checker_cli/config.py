import tomli
import os
from typing import Optional, Set
from pathlib import Path


class Config:
    """Configuration loader from TOML."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.disabled_checks: Set[str] = set()
        if path and os.path.exists(path):
            with open(path, 'rb') as f:
                data = tomli.load(f)
            rules = data.get('rules', {})
            self.disabled_checks = set(rules.get('disable', []))
