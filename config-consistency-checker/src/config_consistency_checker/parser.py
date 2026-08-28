from pathlib import Path
import yaml, tomli, json

def load_config(path: Path):
    if path.suffix in {'.yaml', '.yml'}:
        return yaml.safe_load(path.read_text())
    # ... other formats
    return {}