import pathlib
import shutil
import ipaddress
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import platform
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()

class HostEntry:
    def __init__(self, ip: str, domains: List[str], comment: Optional[str], original_line: str):
        self.ip = ip
        self.domains = domains
        self.comment = comment
        self.original_line = original_line

LineType = str  # 'comment', 'blank', 'host', 'invalid'

class HostsManager:
    def __init__(self):
        self.path = self._get_hosts_path()
        self.lines: List[Dict[str, Any]] = []
        self.backup_dir = pathlib.Path.home() / ".local" / "share" / "local-hosts-manager" / "backups"

    def _get_hosts_path(self) -> pathlib.Path:
        system = platform.system()
        if system in ("Linux", "Darwin"):
            return pathlib.Path("/etc/hosts")
        elif system == "Windows":
            return pathlib.Path(r"C:\Windows\System32\drivers\etc\hosts")
        else:
            raise ValueError(f"Unsupported OS: {system}")

    def load(self) -> None:
        self.lines = []
        try:
            if not self.path.exists():
                self.lines.append({"type": "comment", "content": "# Default hosts file"})
                return
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    self._parse_line(line)
        except Exception as e:
            raise RuntimeError(f"Failed to load {self.path}: {e}")

    def _parse_line(self, line: str) -> None:
        stripped = line.strip()
        if not stripped:
            self.lines.append({"type": "blank"})
            return
        if stripped.startswith("#"):
            self.lines.append({"type": "comment", "content": line.rstrip()})
            return
        hash_pos = line.find("#")
        if hash_pos == -1:
            host_part = line.rstrip()
            comment = None
        else:
            host_part = line[:hash_pos].rstrip()
            comment = line[hash_pos:].lstrip("#").strip()
        host_parts = host_part.split()
        if len(host_parts) < 2:
            self.lines.append({"type": "invalid", "line": line.rstrip()})
            return
        ip = host_parts[0]
        try:
            ipaddress.ip_address(ip)
            domains = host_parts[1:]
            entry = HostEntry(ip, domains, comment, line.rstrip())
            self.lines.append({"type": "host", "entry": entry})
        except ValueError:
            self.lines.append({"type": "invalid", "line": line.rstrip()})

    def backup(self) -> pathlib.Path:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"hosts_{ts}.bak"
        shutil.copy2(self.path, backup_path)
        console.print(f"[green]Backup created: {backup_path}[/green]")
        return backup_path

    def save(self) -> None:
        backup_path = self.backup()
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as f:
                f.write(f"# Hosts managed by local-hosts-manager v{__version__}\n")
                f.write(f"# Backup: {backup_path.name} ({datetime.now().isoformat(timespec='seconds')})\n\n")
                for ln in self.lines:
                    if ln["type"] == "blank":
                        f.write("\n")
                    elif ln["type"] == "comment":
                        f.write(f"{ln['content']}\n")
                    elif ln["type"] == "host":
                        entry = ln["entry"]
                        if not entry.domains:
                            continue
                        entry.domains = sorted(set(entry.domains))  # dedupe/sort
                        f.write(f"{entry.ip}\t{' '.join(entry.domains)}")
                        if entry.comment:
                            f.write(f"\t# {entry.comment}")
                        f.write("\n")
                    elif ln["type"] == "invalid":
                        f.write(f"# Invalid line: {ln['line']}\n")
            temp_path.replace(self.path)
            console.print("[green]Saved successfully.[/green]")
        except PermissionError:
            raise RuntimeError(f"Permission denied writing {self.path}. Run with sudo/admin: sudo local-hosts-manager ...")
        except Exception as e:
            raise RuntimeError(f"Failed to save: {e}")

    def add(self, ip: str, domains: List[str], comment: Optional[str] = None, force: bool = False) -> None:
        try:
            ipaddress.ip_address(ip)
        except ValueError as e:
            raise ValueError(f"Invalid IP '{ip}': {e}")
        conflicts: List[Tuple[str, str]] = []
        for ln in self.lines:
            if ln["type"] == "host":
                entry = ln["entry"]
                for domain in domains:
                    if domain in entry.domains and entry.ip != ip:
                        conflicts.append((domain, entry.ip))
        if conflicts and not force:
            console.print("[yellow]Conflicts:[/yellow]")
            for dom, cip in conflicts:
                console.print(f"  {dom} → {cip} (wanted {ip})")
            if not Confirm.ask("Continue anyway?"):
                raise typer.Exit(0)
        # Update/add to matching IP
        updated = False
        for ln in self.lines:
            if ln["type"] == "host" and ln["entry"].ip == ip:
                for domain in domains:
                    if domain not in ln["entry"].domains:
                        ln["entry"].domains.append(domain)
                updated = True
                break
        if not updated:
            new_entry = HostEntry(ip, list(domains), comment, "")
            self.lines.append({"type": "host", "entry": new_entry})

    def remove(self, domains: List[str]) -> bool:
        removed = False
        for ln in self.lines:
            if ln["type"] == "host":
                before = len(ln["entry"].domains)
                ln["entry"].domains = [d for d in ln["entry"].domains if d.lower() not in [dd.lower() for dd in domains]]
                if len(ln["entry"].domains) < before:
                    removed = True
        if not removed:
            console.print("[yellow]No matching domains found.[/yellow]")
        return removed

    def list(self) -> None:
        table = Table("IP", "Domains", "Comment", title="Hosts Entries")
        for ln in self.lines:
            if ln["type"] == "host" and ln["entry"].domains:
                entry = ln["entry"]
                table.add_row(
                    entry.ip,
                    ", ".join(entry.domains),
                    entry.comment or "",
                )
        console.print(table)

    def stats(self) -> Dict[str, Any]:
        stats = {
            "entries": 0,
            "domains": 0,
            "local": 0,
            "duplicates": set(),
        }
        domain_count: Dict[str, int] = {}
        for ln in self.lines:
            if ln["type"] == "host":
                entry = ln["entry"]
                stats["entries"] += 1
                stats["domains"] += len(entry.domains)
                if entry.ip in ("127.0.0.1", "::1") or entry.ip.startswith(("127.", "::")):
                    stats["local"] += 1
                for d in entry.domains:
                    domain_count[d] = domain_count.get(d, 0) + 1
        for d, cnt in domain_count.items():
            if cnt > 1:
                stats["duplicates"].add(d)
        return stats

    def search(self, pattern: str) -> None:
        table = Table("IP", "Domain", "Comment", title=f"Search '{pattern}'")
        found = False
        for ln in self.lines:
            if ln["type"] == "host":
                entry = ln["entry"]
                for d in entry.domains:
                    if pattern.lower() in d.lower():
                        table.add_row(entry.ip, d, entry.comment or "")
                        found = True
        if found:
            console.print(table)
        else:
            console.print("[yellow]No matches.[/yellow]")

    def validate(self) -> List[str]:
        errors = []
        seen = set()
        for ln in self.lines:
            if ln["type"] == "host":
                entry = ln["entry"]
                for d in entry.domains:
                    if d in seen:
                        errors.append(f"Duplicate domain: {d}")
                    seen.add(d)
        return errors

    def get_backups(self) -> List[pathlib.Path]:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        return sorted(self.backup_dir.glob("*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)

    def list_backups(self) -> None:
        backups = self.get_backups()
        if not backups:
            console.print("[yellow]No backups found.[/yellow]")
            return
        table = Table("File", "Modified", "Size", title="Backups")
        for b in backups[:20]:  # top 20
            stat = b.stat()
            table.add_row(
                b.name,
                datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                f"{stat.st_size:,} B",
            )
        console.print(table)

    def restore(self, filename: str) -> None:
        backup_path = self.backup_dir / filename
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {filename}")
        self.backup()  # backup current first
        shutil.copy2(backup_path, self.path)
        console.print(f"[green]Restored from {filename}[/green]")
