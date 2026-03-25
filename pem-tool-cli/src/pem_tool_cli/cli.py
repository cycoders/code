import typer
import json
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from rich.markdown import Markdown

from .pem_handler import PemHandler
from .types import CertificateInfo, PrivateKeyInfo, CsrInfo

app = typer.Typer(help="Powerful PEM toolkit.", no_args_is_help=True)
console = Console()


@app.command(help="Inspect PEM blocks with rich details.")
def inspect(
    file: Path = typer.Argument(..., help="PEM file"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    with open(file, "r") as f:
        handler = PemHandler(f.read())
    if json_output:
        print(json.dumps(handler.parsed, default=str, indent=2))
        raise typer.Exit()
    _print_table(handler.parsed)


@app.command(help="Validate PEM (expirations, chain consistency).")
def validate(
    file: Path = typer.Argument(..., help="PEM file"),
    password: Optional[str] = typer.Option(None, "--password", help="Key password"),
):
    with open(file, "r") as f:
        handler = PemHandler(f.read(), password.encode() if password else None)
    valid = handler.is_valid_chain()
    status = "[green]✓[/green]" if valid else "[red]✗[/red]"
    console.print(f"Validation: {status} Chain valid")
    if not valid:
        typer.echo("Issues: expirations or issuer mismatch.")


@app.command(help="Compute SHA256 fingerprints.")
def fingerprint(
    file: Path = typer.Argument(..., help="PEM file"),
    json_output: bool = typer.Option(False, "--json"),
):
    with open(file, "r") as f:
        handler = PemHandler(f.read())
    fps = handler.get_fingerprints()
    if json_output:
        print(json.dumps(fps, indent=2))
    else:
        table = Table(title="Fingerprints")
        table.add_column("Block")
        table.add_column("SHA256")
        for k, v in fps.items():
            table.add_row(k, v)
        console.print(table)


@app.command(help="Split multi-block PEM to files.")
def split(
    file: Path = typer.Argument(..., help="Input PEM"),
    output_dir: Path = typer.Option(Path("./"), "--out-dir"),
):
    with open(file, "r") as f:
        handler = PemHandler(f.read())
    output_dir.mkdir(exist_ok=True)
    for i, (typ, body) in enumerate(handler.blocks):
        out_file = output_dir / f"{file.stem}.{i}.{typ.lower().replace(' ', '-')}.pem"
        with open(out_file, "w") as outf:
            outf.write(f"-----BEGIN {typ}-----\n{body}\n-----END {typ}-----\n")
        rprint(f"Wrote: [blue]{out_file}[/blue]")


@app.command(help="Merge PEM files.")
def merge(
    files: List[Path] = typer.Argument(..., help="PEM files to merge"),
    output: Path = typer.Option("merged.pem", "--out"),
):
    content = "\n".join(open(f, "r").read() for f in files)
    with open(output, "w") as f:
        f.write(content)
    rprint(f"Merged to [blue]{output}[/blue]")


@app.command(help="Convert key formats (PKCS1 <-> PKCS8).")
def convert(
    input_file: Path = typer.Argument(..., help="Input"),
    output: Path = typer.Option("converted.pem", "--out"),
    to: str = typer.Option("pkcs8", "--to", help="pkcs8 | pkcs1 | der"),
    password: Optional[str] = typer.Option(None, "--password"),
):
    enc_pass = password.encode() if password else None
    with open(input_file, "r") as f:
        handler = PemHandler(f.read(), enc_pass)
    # Assume single key block for simplicity
    for parsed in handler.parsed.values():
        if isinstance(parsed, PrivateKeyInfo):
            key = serialization.load_pem_private_key(  # Reload for dump
                f"-----BEGIN PRIVATE KEY-----\n...".encode(), enc_pass  # Simplified; in prod reload from block
            )
            if to == "pkcs8":
                format_ = serialization.PrivateFormat.PKCS8
            elif to == "pkcs1":
                format_ = serialization.PrivateFormat.TraditionalOpenSSL
            else:
                raise typer.BadParameter("Unsupported format")
            pem_out = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=format_,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode()
            with open(output, "w") as outf:
                outf.write(pem_out)
            rprint(f"Converted to [blue]{output}[/blue]")
            return
    raise typer.BadParameter("No private key found")


def _print_table(parsed: dict):
    table = Table(title="PEM Inspection", expand=True)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    for block_name, item in parsed.items():
        if isinstance(item, CertificateInfo):
            table.add_row("Block", block_name)
            table.add_row("Type", "Certificate")
            table.add_row("Subject", item.subject)
            table.add_row("Issuer", item.issuer)
            table.add_row("Valid From", item.not_valid_before.isoformat())
            table.add_row("Valid Until", item.not_valid_after.isoformat())
            table.add_row("Serial", item.serial_number)
            table.add_row("Key", f"{item.key_algorithm} {item.key_size}")
            table.add_row("SANs", ", ".join(item.subject_alt_names))
            table.add_row("SHA256 FP", item.sha256_fingerprint)
            table.add_row("")
        elif isinstance(item, PrivateKeyInfo):
            table.add_row("Block", block_name)
            table.add_row("Type", "Private Key")
            table.add_row("Algorithm", item.algorithm)
            table.add_row("Bit Size", str(item.bit_size))
            table.add_row("SHA256 FP", item.sha256_fingerprint)
            table.add_row("")
        # Similar for CSR
    console.print(table)


if __name__ == "__main__":
    app()