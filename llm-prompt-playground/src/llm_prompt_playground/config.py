import os
from pathlib import Path
from typing import Optional

import appdirs
import tomlkit
from pydantic import BaseModel


class Config(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    default_model: str = "gpt-4o-mini"


CONFIG_DIR = Path(appdirs.user_config_dir("llm-prompt-playground"))
CONFIG_PATH = CONFIG_DIR / "config.toml"
HISTORY_PATH = CONFIG_DIR / "history.jsonl"


def load_config() -> Config:
    """Load config from file or env vars."""
    CONFIG_DIR.mkdir(exist_ok=True)

    config_dict = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config_dict = tomlkit.parse(f.read())

    # Override with env
    config_dict["base_url"] = os.getenv("LLM_BASE_URL", config_dict.get("base_url"))
    config_dict["api_key"] = (
        os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", config_dict.get("api_key")))
    )
    config_dict["default_model"] = os.getenv("LLM_DEFAULT_MODEL", config_dict.get("default_model", "gpt-4o-mini"))

    return Config(**config_dict)


def save_config(config: Config) -> None:
    """Save config to file."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write(tomlkit.dumps(config.dict(exclude_unset=True)))
