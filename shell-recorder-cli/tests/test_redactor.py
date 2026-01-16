import re

from shell_recorder_cli.redactor import redact_chunk, redact_session


def test_redact_chunk():
    chunk = "Visit 192.168.1.1 or user@example.com on 2024-01-01"
    redacted = redact_chunk(chunk)
    assert "[REDACTED]" in redacted
    assert "192.168.1.1" not in redacted
    assert "user@example.com" not in redacted
    assert "2024-01-01" not in redacted


def test_redact_session(sample_session, tmp_path):
    out = tmp_path / "redacted.shellrec"
    # Add PII to sample
    with open(sample_session, 'r+') as f:
        data = json.load(f)
        data[2]['stdout'] += '192.168.1.1 '
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    redact_session(sample_session, out)

    with open(out) as f:
        new_data = json.load(f)
    assert "[REDACTED]" in new_data[2]['stdout']
    assert "192.168.1.1" not in new_data[2]['stdout']
