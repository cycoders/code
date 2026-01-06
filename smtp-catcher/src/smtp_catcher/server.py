import asyncio
from aiosmtpd.controller import Controller
from email.parser import BytesParser
import json
from pathlib import Path
from rich.console import Console

from .storage import save_email
from .email_parser import parse_email_parts

console = Console()

class EmailHandler:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    async def handle_DATA(self, server, session, envelope):
        try:
            data = envelope.content  # bytes
            peer = session.peer
            mailfrom = str(envelope.mail_from or "")
            rcpttos = [str(rcpto) for rcpto in envelope.rcpt_tos]

            # Parse MIME
            email_parts = parse_email_parts(data)
            email_dict = {
                "sender": mailfrom,
                "recipients": rcpttos,
                "subject": email_parts["subject"],
                "body_text": email_parts["body_text"],
                "body_html": email_parts["body_html"],
                "headers": email_parts["headers"],
            }

            save_email(self.data_dir, email_dict)
            console.print(
                f"[green]✓ Captured[/] email #{email_dict['recipients']} from '{mailfrom}' re: '{email_dict['subject'][:50]}'"
            )
            return "250 2.0.0 Ok: queued as " + str(len(envelope.content))
        except Exception as e:
            console.print(f"[red]✗ Parse error: {e}[/]")
            return "550 5.3.0 Error"


def start_server(host: str, port: int, data_dir: Path):
    """Start SMTP server (blocks)."""
    handler = EmailHandler(data_dir)
    controller = Controller(
        handler,
        hostname=host,
        port=port,
        authenticator=None,  # No auth
    )
    controller.start()