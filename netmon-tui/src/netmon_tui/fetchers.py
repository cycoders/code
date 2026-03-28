import asyncio
import logging

from typing import List, Dict

import psutil

from .models import Connection, Addr


log = logging.getLogger(__name__)


async def get_connections() -> List[Connection]:
    """Fetch all active TCP/UDP connections (IPv4/IPv6)."""

    connections: List[Connection] = []

    for kind in ("tcp", "udp"):
        for family in ("inet", "inet6"):
            try:
                raw_conns = psutil.net_connections(kind=kind, family=family)
                for raw in raw_conns:
                    if not raw.raddr:
                        continue  # Listening without remote

                    laddr = Addr(raw.laddr.ip, raw.laddr.port)
                    raddr = Addr(raw.raddr.ip, raw.raddr.port)

                    pid = raw.pid
                    proc_name: Optional[str] = None
                    if pid and pid > 0:
                        try:
                            proc_name = psutil.Process(pid).name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass

                    status = raw.status or kind.upper()
                    connections.append(Connection(laddr, raddr, status, pid, proc_name))
            except (OSError, PermissionError) as e:
                log.debug("Failed to fetch %s/%s: %s", kind, family, e)

    return connections


async def get_interface_stats() -> Dict[str, dict]:
    """Fetch per-interface network I/O stats as dicts."""

    try:
        counters = psutil.net_io_counters(pernic=True)
        return {nic: dict(c._asdict()) for nic, c in counters.items()}
    except (OSError, PermissionError) as e:
        log.debug("Failed to fetch interfaces: %s", e)
        return {}