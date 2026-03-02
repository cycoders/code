import concurrent.futures
import ipaddress
import socket
import time
from typing import List, Dict, Any

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn

try:
    from port_scanner_cli.services import identify_service
except ImportError:
    from .services import identify_service

PRESETS = {
    "top100": [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
        1723, 3306, 3389, 5432, 5900, 8080, 8443, 27017, 3000, 5000,
        5433, 5901, 6379, 8081, 9200, 11211, 27017
    ],  # Extended to ~30 popular
    "common": [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 143, 993],
    "web": [80, 443, 8080, 8443, 3000, 5000, 8000],
    "db": [3306, 5432, 6379, 27017, 11211, 9042, 27017],
}


def parse_ports(ports_str: str) -> List[int]:
    """Parse ports string to list of ints."""
    ports_str_lower = ports_str.lower()
    if ports_str_lower in PRESETS:
        return sorted(PRESETS[ports_str_lower])

    ports: List[int] = []
    for part in ports_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                ports.extend(range(max(1, start), min(65536, end + 1)))
            except ValueError:
                raise ValueError(f"Invalid port range: {part}")
        else:
            try:
                p = int(part)
                if 1 <= p <= 65535:
                    ports.append(p)
                else:
                    raise ValueError(f"Port out of range: {p}")
            except ValueError:
                raise ValueError(f"Invalid port: {part}")
    return sorted(set(ports))


def parse_targets(targets_str: str) -> List[str]:
    """Parse targets to list of IPs/hostnames."""
    targets: List[str] = []
    for target in [t.strip() for t in targets_str.split(",") if t.strip()]:
        if "/" in target:
            try:
                network = ipaddress.ip_network(target, strict=False)
                targets.extend(str(ip) for ip in network.hosts())
            except ValueError as e:
                raise ValueError(f"Invalid CIDR: {target} ({e})")
        else:
            targets.append(target)  # Hostname or IP
    return targets


def probe_port(
    ip: str, port: int, timeout: float, grab_banner: bool = False
) -> Dict[str, Any]:
    """Probe single port, return result dict."""
    result: Dict[str, Any] = {
        "ip": ip,
        "port": port,
        "open": False,
        "banner": "",
        "service": "unknown",
        "duration": 0.0,
        "error": "",
    }
    start_time = time.time()
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        result["open"] = True
        result["duration"] = time.time() - start_time
        if grab_banner:
            banner_raw = sock.recv(1024)
            result["banner"] = banner_raw.decode("utf-8", errors="ignore").strip()[:200]
            result["service"] = identify_service(port, result["banner"])
        sock.close()
    except Exception as e:
        result["error"] = str(e)
        result["duration"] = time.time() - start_time
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass
    return result


def scan_ports(
    ips: List[str],
    ports_list: List[int],
    banner: bool,
    max_threads: int,
    timeout: float,
    console,
) -> List[Dict[str, Any]]:
    """Run threaded port scan."""
    results: List[Dict[str, Any]] = []
    open_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning...", total=len(ips) * len(ports_list))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit all
            future_to_probe = {
                executor.submit(probe_port, ip, port, timeout, banner): None
                for ip in ips
                for port in ports_list
            }

            for future in concurrent.futures.as_completed(future_to_probe):
                result = future.result()
                results.append(result)
                progress.advance(task)

                if result["open"]:
                    open_count += 1
                    service = result.get("service", "unknown")
                    banner_prev = result["banner"][:50] + "..." if result["banner"] else ""
                    console.print(
                        f"[green]✓[/] {result['ip']}:{result['port']} [bold cyan]{service}[/bold cyan] "
                        f"[dim]{banner_prev}[/dim]",
                        soft_wrap=True,
                    )

    # Sort opens first
    opens = [r for r in results if r["open"]]
    closed = [r for r in results if not r["open"]]
    return opens + closed