from typing import List, Dict, Optional, Tuple
from email.parser import BytesParser
from email.policy import default
from email.message import EmailMessage
import re
import sys
from io import BytesIO

def parse_email_file_or_stdin(path: str) -> Tuple[EmailMessage, bytes]:
    """Parse EML from file or stdin."""
    if path == "-":
        raw = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as f:
            raw = f.read()
    if not raw:
        raise ValueError("Empty input.")
    msg = BytesParser(policy=default).parsebytes(raw)
    return msg, raw

def extract_received(msg: EmailMessage) -> List[Dict[str, str]]:
    """Extract parsed Received hops (sender-first)."""
    receiveds = msg.get_all("received", [])
    chain = []
    pat = re.compile(
        r"from\s+([^\s\[]+)\s*(\[[^\]]+\])?\s*(?:by\s+[^;]+)?;", re.I
    )
    for line in receiveds:
        m = pat.search(line)
        if m:
            helo = m.group(1).strip()
            ip_match = re.search(r"\[([\d\.\:]+)\]", line)
            ip = ip_match.group(1) if ip_match else "unknown"
            chain.append({"helo": helo, "ip": ip})
    return chain[::-1]  # sender first

def extract_auth_results(msg: EmailMessage) -> List[Dict[str, str]]:
    """Parse Authentication-Results headers."""
    authres = msg.get_all("authentication-results", [])
    parsed = []
    for header in authres:
        parts = [p.strip() for p in header.split(";") if p.strip()]
        res = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                res[k] = v
        if res:
            parsed.append(res)
    return parsed

def get_envelope_info(msg: EmailMessage) -> Dict[str, str]:
    """Extract Return-Path, From domain."""
    return_path = msg.get("return-path", "")
    from_hdr = msg.get("from", "")
    from_domain = re.search(r"@([\w.-]+)", from_hdr)
    from_domain = from_domain.group(1) if from_domain else ""
    return {"return_path": return_path, "from_domain": from_domain}
