import datetime
from datetime import timezone, timedelta

# These are clean
dt1 = datetime.now(tz=timezone.utc)
dt2 = datetime.utcnow(timezone.utc)
dt3 = datetime.fromtimestamp(time.time(), tz=timezone.utc)
dt4 = datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ", tz=timezone.utc)
dt5 = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
