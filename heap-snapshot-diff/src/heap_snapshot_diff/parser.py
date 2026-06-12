from pathlib import Path
import json

def load_snapshot(path: str):
    data = json.loads(Path(path).read_text())
    return {item["type"]: item for item in data}