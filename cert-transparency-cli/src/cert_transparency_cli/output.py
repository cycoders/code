from datetime import datetime, date
from collections import Counter
from dataclasses import asdict
import csv
import json
from io import StringIO
from rich.console import Console
from rich.table import Table
from typing import List

from .models import CertificateEntry

console = Console()

def print_table(entries: List[CertificateEntry]):
    table = Table(title="Certificate Transparency Audit", expand=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Logged", style="magenta")
    table.add_column("Valid From", style="green")
    table.add_column("Valid Until", style="red")
    table.add_column("Days Left", justify="right", style="yellow")
    table.add_column("Issuer", no_wrap=False)
    table.add_column("# SANs", justify="right")
    table.add_column("Sig", no_wrap=True)
    table.add_column("PubKey", no_wrap=True)

    now = datetime.now()
    for e in entries:
        days_left = (e.not_after.date() - now.date()).days
        days_str = str(days_left) if days_left >= 0 else f"[red]{days_left}"
        issuer = e.issuer_name[:40] + "..." if len(e.issuer_name) > 40 else e.issuer_name
        table.add_row(
            str(e.id),
            e.logged_at.strftime("%Y-%m-%d"),
            e.not_before.strftime("%Y-%m-%d"),
            e.not_after.strftime("%Y-%m-%d"),
            days_str,
            issuer,
            str(len(e.subject_alt_names)),
            e.signature_algorithm or "-",
            e.public_key_algorithm or "-",
        )
    console.print(table)

def print_stats(entries: List[CertificateEntry]):
    if not entries:
        return
    now = datetime.now()
    issuers = Counter(e.issuer_name for e in entries)
    table = Table(title="Top Issuers", expand=True)
    table.add_column("Issuer", no_wrap=False)
    table.add_column("Count", justify="right")
    for issuer, count in issuers.most_common(10):
        short = issuer[:50] + "..." if len(issuer) > 50 else issuer
        table.add_row(short, str(count))
    console.print(table)

    buckets = Counter()
    for e in entries:
        days = (e.not_after - now).days
        if days < 0:
            bucket = "Expired"
        elif days < 30:
            bucket = "<30 days"
        elif days < 90:
            bucket = "30-90 days"
        else:
            bucket = ">90 days"
        buckets[bucket] += 1
    exp_table = Table(title="Expiration Distribution", expand=True)
    exp_table.add_column("Bucket")
    exp_table.add_column("Count", justify="right")
    for bucket, count in buckets.most_common():
        exp_table.add_row(bucket, str(count))
    console.print(exp_table)

def output_json(entries: List[CertificateEntry]) -> None:
    data = []
    for e in entries:
        row = asdict(e)
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.isoformat()
        data.append(row)
    print(json.dumps(data, indent=2))

def output_csv(entries: List[CertificateEntry]) -> None:
    if not entries:
        return
    fields = list(asdict(entries[0]).keys())
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for e in entries:
        row = asdict(e)
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.isoformat()
        writer.writerow(row)
    print(output.getvalue().rstrip("\n"))