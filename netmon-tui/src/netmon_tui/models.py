from dataclasses import dataclass

from typing import NamedTuple, Optional


class Addr(NamedTuple):
    """Network address with port."""

    ip: str
    port: Optional[int]


@dataclass(frozen=True)
class Connection:
    """Network connection details."""

    local: Addr
    raddr: Addr
    status: str
    pid: Optional[int]
    process_name: Optional[str]

    def __str__(self) -> str:
        rport = f":{self.raddr.port}" if self.raddr.port else ""
        return f"{self.local.ip}:{self.local.port} → {self.raddr.ip}{rport} [{self.status}]"