from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class Config:
    target_host: str
    target_port: int
    local_port: int
    latency: float  # seconds
    jitter: float  # seconds
    loss: float  # 0-1
    dup: float  # 0-1
    bw_kbps: float  # kbps

    @property
    def bw_bytes_per_sec(self) -> float:
        return self.bw_kbps * 125.0  # 1000/8


def parse_duration(value: str) -> float:
    """Parse '100ms', '1s' -> seconds."""
    value = value.strip().lower()
    if value.endswith("ms"):
        return float(value[:-2]) / 1000
    elif value.endswith("s"):
        return float(value[:-1])
    else:
        return float(value)


def parse_bw(value: str) -> float:
    """Parse '100', 'inf', '100kbps' -> kbps."""
    value = value.strip().lower()
    if value in ("inf", "infty"):
        return float("inf")
    mult = 1.0
    if value.endswith("kbps"):
        mult = 1.0
        value = value[:-4]
    return float(value) * mult


def load_config_from_cli(
    target: str,
    local_port: int,
    latency: str,
    jitter: str,
    loss: float,
    dup: float,
    bw: str,
) -> Config:
    host, port_str = target.rsplit(":", 1)
    return Config(
        target_host=host,
        target_port=int(port_str),
        local_port=local_port,
        latency=parse_duration(latency),
        jitter=parse_duration(jitter),
        loss=loss,
        dup=dup,
        bw_kbps=parse_bw(bw),
    )


def load_config_from_yaml(path: str) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return Config(
        target_host=data["target_host"],
        target_port=int(data["target_port"]),
        local_port=data.get("local_port", 8080),
        latency=parse_duration(data["latency"]),
        jitter=parse_duration(data["jitter"]),
        loss=data.get("loss", 0.0),
        dup=data.get("dup", 0.0),
        bw_kbps=parse_bw(data["bw"]),
    )
