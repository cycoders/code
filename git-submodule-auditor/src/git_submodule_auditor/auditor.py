import os
import re
import time
import git
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from .models import Submodule


class Auditor:
    """Core auditor for Git submodules. Handles parsing, analysis, cycles, graphs."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        try:
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            raise ValueError("Not a valid Git repository. Run from repo root.")
        self.submodules_raw = list(self.repo.submodules)
        if not self.submodules_raw:
            console = Console()
            console.print("[yellow]No submodules found.[/yellow]")
        self.status_map = self._parse_status()
        self.submodules = self._populate_submodules()
        self.cycles = self._find_cycles()

    def _parse_status(self) -> Dict[str, Dict]:
        """Parse `git submodule status` output."""
        try:
            status_out = self.repo.git.submodule_status()
        except git.GitCommandError:
            return {}
        status_map = {}
        for line in status_out.splitlines():
            line = line.strip()
            if not line:
                continue
            # Match: [+- ]SHA path (branch -> SHA)
            match = re.match(r'^([+\-\s]?)([0-9a-f]{40})\s+(.*?)(?:\s+\((.*?)\))?$', line)
            if match:
                prefix = match.group(1)
                sha = match.group(2)
                path = match.group(3).strip()
                status_map[path] = {'prefix': prefix, 'sha': sha}
        return status_map

    def _populate_submodules(self) -> List[Submodule]:
        subs = []
        for sm in self.submodules_raw:
            status = self.status_map.get(sm.path, {'prefix': ''})
            prefix = status['prefix']
            is_dirty = '+' in prefix
            outdated = '-' in prefix
            issues = self._get_base_issues(sm, prefix)
            age_days = self._get_commit_age(sm.hexsha)
            if age_days > 180:
                issues.append('old-commit')
            # Check remote
            target_branch = sm.branch.name if sm.branch else None
            if target_branch:
                latest = self._get_latest_commit(sm, target_branch)
                if latest != sm.hexsha:
                    outdated = True
                    issues.append('outdated-remote')
            sub = Submodule(
                path=sm.path,
                url=sm.url,
                current_commit=sm.hexsha,
                target_branch=target_branch,
                is_dirty=is_dirty,
                outdated=outdated,
                days_behind=age_days,
                issues=issues
            )
            subs.append(sub)
        return subs

    def _get_base_issues(self, sm: git.Submodule, prefix: str) -> List[str]:
        issues = []
        if '+' in prefix:
            issues.append('dirty')
        if not sm.branch:
            issues.append('no-branch')
        if not sm.url.startswith('https://'):
            issues.append('insecure-url')
        return issues

    def _get_commit_age(self, commit: str) -> int:
        try:
            ts_str = self.repo.git.rev_list('--max-count=1', '--format=%ct', commit).strip()
            ts = int(ts_str)
            return int((time.time() - ts) / 86400.0)
        except:
            return 0

    def _get_latest_commit(self, sm: git.Submodule, branch_name: str) -> str:
        try:
            ref_lines = sm.git.ls_remote(sm.url, f"refs/heads/{branch_name}").splitlines()
            for line in ref_lines:
                parts = line.split()
                if len(parts) == 2 and parts[1] == f"refs/heads/{branch_name}":
                    return parts[0]
        except:
            pass
        return sm.hexsha

    def _find_cycles(self) -> List[str]:
        cycles = []
        def dfs(curr_path: str, stack: List[str]):
            if curr_path in stack:
                start = stack.index(curr_path)
                cycles.append(" -> ".join(stack[start:]))
                return
            try:
                sub_path = os.path.join(self.repo_path, curr_path)
                sub_repo = git.Repo(sub_path)
                for sm in sub_repo.submodules:
                    dfs(os.path.join(curr_path, sm.path), stack + [curr_path])
            except Exception:
                pass
        for sm in self.submodules_raw:
            dfs(sm.path, [])
        return cycles

    def generate_mermaid(self) -> str:
        graph = "graph TD\n    root((Root))\n"
        def add_edges(curr: str):
            node_id = curr.replace(os.sep, '_').replace('.', '_')
            try:
                sub_path = os.path.join(self.repo_path, curr)
                sub_repo = git.Repo(sub_path)
                for sm in sub_repo.submodules:
                    child_id = os.path.join(curr, sm.path).replace(os.sep, '_').replace('.', '_')
                    graph += f"    {node_id} --> {child_id}\n"
                    add_edges(os.path.join(curr, sm.path))
            except Exception:
                pass
        for sm in self.submodules_raw:
            node_id = sm.path.replace(os.sep, '_').replace('.', '_')
            graph += f"    root --> {node_id}\n"
            add_edges(sm.path)
        return graph

    def print_list(self, console: Console):
        table = Table(title="Git Submodules")
        table.add_column("Path", style="cyan")
        table.add_column("Branch")
        table.add_column("Commit", style="green")
        table.add_column("Status")
        for sm in self.submodules_raw:
            status = self.status_map.get(sm.path, {}).get('prefix', '?')
            branch = sm.branch.name if sm.branch else "detached"
            table.add_row(sm.path, branch, sm.hexsha[:8], status)
        console.print(table)

    def print_audit(self, console: Console):
        if self.cycles:
            console.print("[bold red]⚠️  Cycles detected:[/bold red]")
            for cycle in self.cycles:
                console.print(f"  [red]{cycle}[/red]")
        table = Table(title="Audit Report")
        table.add_column("Path")
        table.add_column("Issues", style="yellow")
        table.add_column("Days Behind")
        table.add_column("Outdated", style="red")
        for sub in self.submodules:
            issues_str = ', '.join(sub.issues) if sub.issues else '[green]OK[/green]'
            outdated_str = '[red]Yes[/red]' if sub.outdated else '[green]No[/green]'
            table.add_row(sub.path, issues_str, str(sub.days_behind), outdated_str)
        console.print(table)
