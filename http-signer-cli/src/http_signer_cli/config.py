import tomllib
from pathlib import Path
import platformdirs

def get_config_path() -> Path:
    config_dir = platformdirs.user_config_dir("http-signer-cli")
    Path(config_dir).mkdir(parents=True, exist_ok=True)
    return Path(config_dir) / "config.toml"

def get_credentials(profile: str, scheme: str) -> dict:
    """Load credentials from profile for scheme."""
    config_path = get_config_path()
    if not config_path.exists():
        raise typer.Exit(
            f"Config not found at {config_path}. Create it or use flags."
        )
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    profiles = data.get("profiles", {})
    creds = profiles.get(profile, {})
    return creds.get(scheme, {})