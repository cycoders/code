import json
import re
from pathlib import Path
from typing import List, Dict, Any

from .utils import shannon_entropy, mask_snippet


PATTERNS: List[Dict[str, Any]] = [
    {"id": "aws_access_key_id", "name": "AWS Access Key ID", "regex": r"AKIA[0-9A-Z]{16}"},
    {"id": "aws_secret_access_key", "name": "AWS Secret Access Key", "regex": r"[0-9a-zA-Z/+]{40}"},
    {"id": "google_api_key", "name": "Google API Key", "regex": r"AIza[0-9A-Za-z\-_]{35}"},
    {"id": "github_token", "name": "GitHub Token", "regex": r"gh[pouso_][0-9a-zA-Z]{36,40}"},
    {"id": "github_pat", "name": "GitHub PAT", "regex": r"ghp_[0-9a-zA-Z]{36}"},
    {"id": "slack_token", "name": "Slack Token", "regex": r"xox[baprs]-[0-9a-zA-Z]{10,48}"},
    {"id": "jwt", "name": "JWT Token", "regex": r"eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+"},
    {"id": "private_key", "name": "Private Key", "regex": r"-----BEGIN [A-Z]+ PRIVATE KEY-----"},
    {"id": "stripe_key", "name": "Stripe API Key", "regex": r"sk_live_[0-9a-zA-Z]{24}"},
    {"id": "facebook_oauth", "name": "Facebook OAuth", "regex": r"EAA[0-9A-Za-z]+"},
    {"id": "twilio_api", "name": "Twilio API Key", "regex": r"SK[a-f0-9]{32}"},
    {"id": "paypal_braintree", "name": "PayPal Braintree", "regex": r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}"},
    {"id": "square_access", "name": "Square Token", "regex": r"sq0atp-[0-9A-Za-z\-_]{22}"},
    {"id": "sendgrid_key", "name": "SendGrid API Key", "regex": r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}"},
    {"id": "heroku_api", "name": "Heroku API Key", "regex": r"[hH][eE][rR][oO][kK][uU]\.[0-9A-F]{8}[0-9A-F]{4}[0-9A-F]{4}[0-9A-F]{4}[0-9A-F]{12}"},
]


def load_patterns(patterns_file: str | None = None) -> List[Dict[str, Any]]:
    """Load patterns from file or use built-ins."""
    if patterns_file and Path(patterns_file).exists():
        with open(patterns_file) as f:
            custom = json.load(f)
        return custom
    return PATTERNS


def detect_in_text(
    text: str,
    patterns: List[Dict[str, Any]],
    entropy_thresh: float,
    min_length: int,
    allowlist: List[str],
) -> List["Detection"]:
    """Detect secrets in text."""
    hits: List[Detection] = []
    lines = text.splitlines()

    # Regex detectors
    for pat in patterns:
        regex = re.compile(pat["regex"], re.IGNORECASE | re.MULTILINE)
        for line_num, line in enumerate(lines, 1):
            for match in regex.finditer(line):
                snippet = mask_snippet(line)
                if any(re.search(al, snippet, re.I) for al in allowlist):
                    continue
                hits.append(Detection(pat["id"], pat["name"], line_num, snippet))

    # Entropy detector
    for line_num, line in enumerate(lines, 1):
        line_str = line.strip()
        if len(line_str) >= min_length:
            ent = shannon_entropy(line_str)
            if ent >= entropy_thresh:
                snippet = mask_snippet(line_str)
                if not any(re.search(al, snippet, re.I) for al in allowlist):
                    hits.append(Detection("high_entropy", "High Entropy String", line_num, snippet, ent))

    return hits