import os
import sys
import time
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
from rich.console import Console
import psutil
import tracemalloc

from .analyzer import analyze_rss, analyze_heap_diffs

WRAPPER_TEMPLATE = '''
import os
import sys
import time
from pathlib import Path
import tracemalloc
from threading import Thread, Event
import runpy

tempdir = os.environ["MEMLEAK_TEMPDIR"]
tracemalloc.start(nframe=5)

snap_count = 0
def take_snapshot():
    global snap_count
    snap_count += 1
    path = Path(tempdir) / f"snapshot_{snap_count:03d}.pytrace"
    tracemalloc.take_snapshot().dump(str(path))

user_thread: Thread | None = None

cmd_file = Path(tempdir) / "cmd"

def poller():
    global user_thread
    while user_thread and user_thread.is_alive():
        if cmd_file.exists():
            try:
                cmd_file.unlink()
            except FileNotFoundError:
                pass
            take_snapshot()
        time.sleep(0.5)

def run_user_script():
    script_path = sys.argv[1]
    args = sys.argv[2:]
    runpy.run_path(script_path, run_name="__main__", argv=[script_path] + args)

if __name__ == "__main__":
    global user_thread
    user_thread = Thread(target=run_user_script, daemon=False)
    user_thread.start()
    poll_thread = Thread(target=poller, daemon=True)
    poll_thread.start()
    user_thread.join()
'''

def monitor_script(
    console: Console,
    script: Path,
    args: List[str],
    duration: float,
    interval: float,
    rss_thresh_bytes: float,
    heap_thresh_bytes: int,
    output_dir: Optional[Path],
) -> None:
    if not script.exists():
        typer.echo(f"Error: Script {script} not found.", err=True)
        raise typer.Exit(1)

    is_temp = output_dir is None
    if is_temp:
        temp_dir_obj = tempfile.TemporaryDirectory(prefix="memleak_")
        session_dir = Path(temp_dir_obj.name)
    else:
        session_dir = output_dir
        session_dir.mkdir(exist_ok=True)

    try:
        wrapper_path = session_dir / "wrapper.py"
        wrapper_path.write_text(WRAPPER_TEMPLATE)

        env = os.environ.copy()
        env["MEMLEAK_TEMPDIR"] = str(session_dir)

        cmd = [sys.executable, str(wrapper_path), str(script), *args]
        p = subprocess.Popen(
            cmd,
            env=env,
            cwd=script.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            proc = psutil.Process(p.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            console.print("[red]Failed to access process.[/red]")
            return

        rss_history: List[float] = []
        timestamps: List[float] = []
        start_time = time.time()

        cmd_file = session_dir / "cmd"

        while True:
            elapsed = time.time() - start_time
            if duration > 0 and elapsed > duration:
                break

            # Trigger snapshot
            cmd_file.touch()

            # RSS
            try:
                mem = proc.memory_info()
                rss_bytes = mem.rss
                rss_mb = rss_bytes / (1024 ** 2)
                rss_history.append(rss_mb)
                timestamps.append(elapsed)
            except psutil.NoSuchProcess:
                break

            time.sleep(interval)

        # Graceful shutdown
        p.send_signal(subprocess.signal.SIGTERM)
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()

    finally:
        if is_temp:
            shutil.rmtree(session_dir, ignore_errors=True)

    # Analyze
    snapshot_paths = sorted(session_dir.glob("snapshot_*.pytrace"))
    if not snapshot_paths:
        console.print("[yellow]No snapshots captured.[/yellow]")
        return

    snapshots = [tracemalloc.Snapshot.load(str(p)) for p in snapshot_paths]

    rss_analysis = analyze_rss(rss_history, timestamps, rss_thresh_bytes / (1024**2))
    heap_analysis = analyze_heap_diffs(snapshots, heap_thresh_bytes)

    # Save session
    session_dir.mkdir(exist_ok=True)
    import json
    (session_dir / "rss_history.json").write_text(
        json.dumps({"timestamps": timestamps, "rss_mb": rss_history})
    )
    console.print(f"[green]Session saved: {session_dir}[/green]")

    from .reporter import print_report
    print_report(console, rss_analysis, heap_analysis)
