from pathlib import Path
import tomlkit

def load_config(config_path: Path) -> dict:
    """Load configuration from TOML file."""
    try:
        content = tomlkit.parse(config_path.read_text())
        # Flatten container to dict
        return {k: v.as_primitive() if hasattr(v, "as_primitive") else v for k, v in content.items()}
    except (tomlkit.TOMLDecodeError, FileNotFoundError, PermissionError):
        return {}