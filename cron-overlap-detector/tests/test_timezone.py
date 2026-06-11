from datetime import datetime, timezone

def test_utc_handling():
    assert datetime.now(timezone.utc).tzinfo is not None