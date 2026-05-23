import hashlib
import json
from pathlib import Path

class ContentCache:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def key(self, task_name: str, signature: dict) -> str:
        return hashlib.sha256(json.dumps({task_name: signature}, sort_keys=True).encode()).hexdigest()

    def hit(self, key: str) -> bool:
        return (self.root / key).exists()