from email.parser import BytesParser
from email import policy
from typing import Dict, Any, Optional


def parse_email_parts(data: bytes) -> Dict[str, Any]:
    """
    Parse raw SMTP data (bytes) into structured parts.
    Handles multipart, extracts text/html, headers.
    """
    msg = BytesParser(policy=policy.default).parsebytes(data)
    headers = dict(msg.items())

    subject = headers.get("subject", "")
    body_text: Optional[str] = None
    body_html: Optional[str] = None

    if msg.is_multipart():
        for part in msg.iter_parts():
            ctype = part.get_content_type()
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            try:
                decoded = payload.decode("utf-8", errors="ignore")
            except:
                decoded = "(decode error)"
            if ctype == "text/plain":
                body_text = decoded
            elif ctype == "text/html":
                body_html = decoded
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            try:
                decoded = payload.decode("utf-8", errors="ignore")
            except:
                decoded = "(decode error)"
            ctype = msg.get_content_type()
            if "html" in ctype:
                body_html = decoded
            else:
                body_text = decoded

    return {
        "subject": subject,
        "body_text": body_text,
        "body_html": body_html,
        "headers": headers,
    }