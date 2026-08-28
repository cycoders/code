from pathlib import Path
import yaml, tomli, json

def load(path: Path):
    if path.suffix in {'.yaml', '.yml'}:
        return yaml.safe_load(path.read_text())
    if path.suffix == '.toml':
        return tomli.loads(path.read_text())
    if path.suffix == '.json':
        return json.loads(path.read_text())
    raise ValueError(f"Unsupported format: {path.suffix}")