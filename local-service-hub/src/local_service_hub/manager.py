import json
import os
import subprocess
import time
from pathlib import Path
import jinja2
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress

from .config import load_config, merge_configs
from .services import DEFAULT_SERVICES

console = Console()

data_dir = Path.cwd() / ".local-service-hub"
compose_file = data_dir / "docker-compose.yml"
templates_dir = Path(__file__).parent.parent / "templates"
project_name = f"lsh-{Path.cwd().name.replace('/', '-', 1).split('/')[0][:8]}"

docker_args = ["docker", "compose", "--project-name", project_name, "-f", str(compose_file)]


def get_effective_services() -> Dict[str, Dict[str, Any]]:
    config = load_config()
    effective: Dict[str, Dict[str, Any]] = {}
    for name, default in DEFAULT_SERVICES.items():
        user_cfg = config.get("services", {}).get(name, {})
        merged = merge_configs(default, user_cfg)
        merged["enabled"] = user_cfg.get("enabled", True)
        if merged["enabled"]:
            effective[name] = merged
    return effective


def generate_compose():
    """Render docker-compose.yml from template."""
    data_dir.mkdir(exist_ok=True)
    effective_services = get_effective_services()

    with open(templates_dir / "docker-compose.yml.j2") as f:
        template = jinja2.Template(f.read())

    yml_content = template.render(services=effective_services)
    with open(compose_file, "w") as f:
        f.write(yml_content)


def run_docker(*args: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    cmd = [*docker_args, *args]
    try:
        return subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error: {e.stderr or e.stdout}", file=console.stderr)
        raise


def get_ports_map(service: str, container_ports: List[str]) -> Dict[str, str]:
    ports_map: Dict[str, str] = {}
    for cp in container_ports:
        try:
            out = subprocess.check_output([*docker_args, "port", service, cp], text=True).strip()
            host_port = out.split(':')[-1].rsplit('/')[0]
            ports_map[cp] = host_port
        except subprocess.CalledProcessError:
            ports_map[cp] = cp  # fallback
    return ports_map


def print_env(service: str):
    effective_services = get_effective_services()
    if service not in effective_services:
        console.print(f"[red]Service '{service}' not enabled.")
        return

    svc = effective_services[service]
    ports_map = get_ports_map(service, svc["container_ports"])

    format_dict = svc.get("environment", {}).copy()
    format_dict.update({f"port_{cp}": ports_map.get(cp, cp) for cp in svc["container_ports"]})

    console.print("[bold cyan]Environment vars:[/]")
    for key, template in svc.get("env_vars", {}).items():
        try:
            value = template.format(**format_dict)
            console.print(f"  [green]{key}[/]=[blue]{value}[/]"]
        except KeyError as e:
            console.print(f"  [yellow]{key}[/]: template error {{e}}")


def status(live: bool = False):
    generate_compose()
    table = Table(title="Local Service Hub Status", show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Ports", style="yellow")
    table.add_column("Container", style="dim", width=20)

    def update_table():
        table.clear_rows()
        result = run_docker("ps", "--format", "json", check=False, capture_output=True)
        if result.returncode != 0 or not result.stdout.strip():
            console.print("[yellow]No services running or compose not generated.")
            return
        ps_list = json.loads(result.stdout)
        for entry in ps_list:
            svc_name = entry["Name"].rsplit("_", 1)[-1]
            status_full = entry["Status"]
            ports = entry["Ports"] or "-"
            table.add_row(svc_name, status_full, ports, entry["Name"])

    update_table()
    console.print(table)

    if live:
        with Live(table, refresh_per_second=0.5, screen=True) as live_display:
            try:
                while True:
                    time.sleep(2)
                    update_table()
                    live_display.update(table)
            except KeyboardInterrupt:
                console.print("\n[green]Status monitoring stopped.")


def up(services: Optional[List[str]] = None):
    generate_compose()
    effective = get_effective_services()
    if services is None:
        services = list(effective)
    else:
        services = [s for s in services if s in effective]

    if not services:
        console.print("[yellow]No services to start.")
        return

    with Progress() as progress:
        pull_task = progress.add_task("[cyan]Pulling images...", total=None)
        run_docker("pull")
        progress.remove_task(pull_task)

        for svc in services:
            task = progress.add_task(f"[green]Starting {svc}...", total=None)
            run_docker("up", "-d", svc)
            progress.remove_task(task)

    console.print(f"[bold green]Started: {', '.join(services)}")


def down(services: Optional[List[str]] = None):
    generate_compose()
    effective = get_effective_services()
    if services is None:
        services = list(effective)
    else:
        services = [s for s in services if s in effective]

    for svc in services:
        run_docker("down", svc)
    console.print(f"[bold green]Stopped: {', '.join(services)}")


def logs(service: str, follow: bool = True, tail: Optional[int] = None):
    args = ["logs"]
    if follow:
        args.append("-f")
    if tail:
        args.extend(["--tail", str(tail)])
    args.append(service)
    run_docker(*args, check=False)


def connect(service: str):
    effective = get_effective_services()
    if service not in effective:
        console.print(f"[red]Service '{service}' not available.")
        return
    cmd = effective[service].get("connect_cmd", [])
    full_cmd = [*docker_args, "exec", "-it", service, *cmd]
    os.execvp("docker", full_cmd)
