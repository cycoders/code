'''Language-specific code normalizers.''' 

from pathlib import Path
import subprocess
import typer
from rich.console import Console

console = Console()

PRETTIER_EXTS = {'.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml', '.md', '.css', '.scss', '.html'}
PRETTIER_PARSERS = {
    '.js': 'babel',
    '.jsx': 'babel',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.css': 'css',
    '.scss': 'scss',
    '.html': 'html',
}

def normalize_content(filepath: str, content: str) -> str:
    """Normalize content using the appropriate formatter. Falls back to original if unavailable."""
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext == '.py':
        try:
            from black import format_file_contents, Mode
            result = format_file_contents(
                content,
                fast=False,
                mode=Mode.PREVIEW,
            )
            return result[0]
        except Exception as e:
            console.print(f"[yellow]Black failed for {filepath}: {e}[/]")
            return content

    elif ext == '.go':
        try:
            proc = subprocess.run(
                ['gofmt'],
                input=content.encode('utf-8'),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            return proc.stdout
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            console.print(f"[yellow]gofmt failed for {filepath}: {e}[/]")
            return content

    elif ext == '.rs':
        try:
            proc = subprocess.run(
                ['rustfmt', '--edition', '2021'],
                input=content.encode('utf-8'),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            return proc.stdout
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            console.print(f"[yellow]rustfmt failed for {filepath}: {e}[/]")
            return content

    elif ext in PRETTIER_EXTS:
        parser = PRETTIER_PARSERS.get(ext, 'babel')
        try:
            proc = subprocess.run(
                ['prettier', '--stdin-filepath', filepath, '--parser', parser],
                input=content.encode('utf-8'),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            return proc.stdout
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            console.print(f"[yellow]Prettier failed for {filepath}: {e}[/]")
            return content

    return content  # No formatter
