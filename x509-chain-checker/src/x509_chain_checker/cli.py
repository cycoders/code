import typer
from pathlib import Path
from typing import Annotated, Optional

from x509_chain_checker import __version__
from x509_chain_checker.validator import Validator
from x509_chain_checker.root_stores import load_trusted_roots
from x509_chain_checker.cert_utils import load_cert, load_certs_from_dir
from x509_chain_checker.reporter import report

app = typer.Typer(help="Offline X.509 certificate chain checker", add_completion=False)


@app.command()
def validate(
    cert: Path = typer.Argument(..., help="Leaf certificate (PEM/DER)"),
    intermediates: Annotated[Optional[List[Path]], typer.Argument(None, help="Intermediate certs or dir")] = None,
    roots: Optional[Path] = typer.Option(None, "--roots", help="Custom roots path/dir/bundle"),
    purpose: str = typer.Option("server", "--purpose", help="server/client/ca/any"),
    output: str = typer.Option("rich", "--output/-o", help="rich/json/html"),
    out_file: Optional[Path] = typer.Option(None, "--file/-f", help="Output file"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
):
    """Validate certificate chain."""
    if verbose:
        typer.echo(f"Validating {cert} (purpose: {purpose})\n")

    try:
        leaf = load_cert(cert)
    except Exception as e:
        typer.echo(f"Error loading cert: {e}", err=True)
        raise typer.Exit(1)

    inter_certs = []
    if intermediates:
        for p in intermediates:
            if p.is_dir():
                inter_certs.extend(load_certs_from_dir(p))
            else:
                inter_certs.append(load_cert(p))

    pool = inter_certs + load_trusted_roots(roots)
    validator = Validator(purpose)
    chain = validator.build_chain(leaf, pool)
    report_data = validator.validate(chain, load_trusted_roots(roots))

    report(output, report_data, out_file)
    if report_data.overall_status == "invalid":
        raise typer.Exit(2)


@app.command()
def roots(
    sub: str = typer.Argument("list"),
    roots_dir: Optional[Path] = typer.Option(Path("~/.x509-chain-checker/roots"), "--roots-dir"),
):
    """Manage root stores."""
    roots_dir = roots_dir.expanduser()
    roots_dir.mkdir(exist_ok=True)

    if sub == "update":
        from urllib.request import urlopen
        cacert_url = "https://curl.se/ca/cacert.pem"
        typer.echo(f"Downloading roots to {roots_dir / 'cacert.pem'}...")
        try:
            with urlopen(cacert_url) as resp:
                with open(roots_dir / "cacert.pem", "wb") as f:
                    f.write(resp.read())
            typer.echo("✅ Updated!")
        except Exception as e:
            typer.echo(f"❌ Failed: {e}")
            raise typer.Exit(1)
    elif sub == "list":
        roots = load_trusted_roots(roots_dir)
        typer.echo(f"Loaded {len(roots)} roots from {roots_dir}")
        for r in roots[:10]:
            cn = r.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            typer.echo(f"  - {cn[0].value if cn else 'No CN'}")


@app.command()
def version():
    typer.echo(f"x509-chain-checker {__version__}")


if __name__ == "__main__":
    app()