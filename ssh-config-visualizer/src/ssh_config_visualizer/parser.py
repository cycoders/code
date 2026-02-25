import io
import os
from pathlib import Path
from typing import List

from paramiko.ssh_config import SSHConfig
from ssh_config_visualizer import SSHHost


def load_ssh_config(config_path: str | Path = "~/.ssh/config") -> SSHConfig:
    """Load and parse SSH config file."""
    config_path = Path(config_path).expanduser()
    if not config_path.exists():
        raise FileNotFoundError(f"SSH config not found: {config_path}")

    ssh_config = SSHConfig()
    with open(config_path, "r", encoding="utf-8") as f:
        ssh_config.parse(f)
    return ssh_config


def parse_config_content(content: str) -> List[SSHHost]:
    """Parse SSH config from string content (for tests)."""
    ssh_config = SSHConfig()
    ssh_config.parse(io.StringIO(content))
    return get_all_host_sections(ssh_config)


def get_all_host_sections(ssh_config: SSHConfig) -> List[SSHHost]:
    """Extract all Host sections as SSHHost objects."""
    # Note: _config is 'private' but stable API in paramiko
    sections = ssh_config._config._sections  # type: ignore[reportPrivateUsage]

    hosts: List[SSHHost] = []
    for pattern, raw_config in sections.items():
        config = {}
        for opt, val in raw_config.items():
            if isinstance(val, list):
                config[opt] = val
            else:
                config[opt] = [str(val)] if val else []
        hosts.append(SSHHost(pattern=pattern, config=config))
    return hosts


class SSHHost:
    """Parsed SSH Host block."""

    def __init__(self, pattern: str, config: dict[str, list[str]]):
        self.pattern = pattern
        self.config = config

    def __repr__(self) -> str:
        return f"SSHHost(pattern='{self.pattern}', hostname={self.config.get('hostname')})"