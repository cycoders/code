import ast
import fnmatch
import shutil
import subprocess
import tempfile
from collections import defaultdict, Counter
from pathlib import Path
from typing import Iterator, List, Dict

from rich.progress import Progress
from rich.table import Table
from rich.console import Console

import mutation_tester.mutator as mutator
from mutation_tester.types import Config, MutantLocation, MutantResult


console = Console()


def find_pyfiles(root: Path, exclude_patterns: List[str]) -> Iterator[Path]:
    """Find all .py files, skipping excluded patterns and dotdirs."""
    for path in root.rglob("*.py"):
        rel = str(path.relative_to(root))
        if (
            path.parent.name.startswith(".")
            or any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(path.name, pat) for pat in exclude_patterns)
        ):
            continue
        yield path


def ignore_func(exclude_patterns: List[str]):
    """Shutil ignore func."""
    def _ignore(directory: Path, files: List[str]):
        return [f for f in files if any(fnmatch.fnmatch(f, p) for p in ["__pycache__", "venv", ".git"] + exclude_patterns)]
    return _ignore


def run_pytest(temp_base: Path, cfg: Config) -> tuple[bool, bool]:
    """Run pytest on temp project. Returns (killed, timed_out)."""
    cmd = ["pytest"] + cfg.pytest_args + [str(temp_base)]
    try:
        result = subprocess.run(cmd, cwd=temp_base, timeout=cfg.timeout_secs, capture_output=True, text=True)
        return result.returncode != 0, False
    except subprocess.TimeoutExpired:
        return False, True  # conservative: not killed
    except FileNotFoundError:
        raise RuntimeError("pytest command not found. Ensure 'pytest' is installed and on PATH.")


def run_mutations(target_dir: Path, cfg: Config, dry_run: bool) -> Dict[str, Any]:
    """Run full mutation testing suite."""
    pyfiles = list(find_pyfiles(target_dir, cfg.exclude_patterns))
    all_mutants: List[MutantLocation] = []
    for pyfile in pyfiles:
        rel = pyfile.relative_to(target_dir)
        mutants = mutator.collect_mutants(pyfile)
        for m in mutants:
            m["rel_path"] = rel
        all_mutants.extend(mutants)

    if not all_mutants:
        raise RuntimeError("No mutants found. Check for Python files or add more code.")

    if dry_run:
        console.print(f"[green]Dry-run: Found {len(all_mutants)} mutants across {len(pyfiles)} files.")
        return {"dry_run": True}

    all_mutants = all_mutants[: cfg.max_mutants]
    console.print(f"[yellow]Testing {len(all_mutants)} mutants...")

    with tempfile.TemporaryDirectory() as tmpdir_str:
        temp_base = Path(tmpdir_str)
        shutil.copytree(target_dir, temp_base, ignore=ignore_func(cfg.exclude_patterns))

        results: List[MutantResult] = []
        with Progress() as progress:
            task = progress.add_task("[cyan]Killing mutants...", total=len(all_mutants))
            for mut in all_mutants:
                rel_path = Path(mut["rel_path"])
                temp_file = temp_base / rel_path
                orig_source = temp_file.read_text(errors="ignore")
                killed = False
                timed_out = False
                try:
                    tree = ast.parse(orig_source)
                    transformer = mut["transformer_cls"](mut)
                    mutated_tree = transformer.visit(tree)
                    ast.fix_missing_locations(mutated_tree)
                    mutant_source = ast.unparse(mutated_tree)
                    temp_file.write_text(mutant_source)
                    killed, timed_out = run_pytest(temp_base, cfg)
                except Exception:
                    killed = True  # syntax error = killed
                finally:
                    temp_file.write_text(orig_source)

                results.append({"file": rel_path, "mut_id": mut["mut_id"], "killed": killed, "timed_out": timed_out})
                progress.advance(task)

    return make_results(results)


def make_results(results: List[MutantResult]) -> Dict[str, Any]:
    """Aggregate results into stats and table."""
    file_stats = defaultdict(lambda: {"total": 0, "killed": 0, "survived": 0, "timedout": 0})
    for r in results:
        stats = file_stats[r["file"].as_posix()]
        stats["total"] += 1
        if r["timed_out"]:
            stats["timedout"] += 1
        elif r["killed"]:
            stats["killed"] += 1
        else:
            stats["survived"] += 1

    table = Table(title="[bold cyan]Mutation Test Results")
    table.add_column("File", style="cyan")
    table.add_column("Total")
    table.add_column("Killed", style="green")
    table.add_column("Survived", style="red")
    table.add_column("Timeout", style="yellow")
    table.add_column("Score", justify="right")

    total_total = total_killed = 0
    for fname, stats in sorted(file_stats.items()):
        score = (stats["killed"] / stats["total"] * 100) if stats["total"] else 0
        table.add_row(fname, str(stats["total"]), str(stats["killed"]), str(stats["survived"]), str(stats["timedout"]), f"{score:.1f}%")
        total_total += stats["total"]
        total_killed += stats["killed"]

    overall_score = (total_killed / total_total * 100) if total_total else 0
    table.add_row("[bold]OVERALL[/bold]", str(total_total), str(total_killed), "", "", f"[bold]{overall_score:.1f}%[/bold]")

    return {
        "table": table,
        "overall_score": overall_score,
        "total_mutants": total_total,
        "killed": total_killed,
    }