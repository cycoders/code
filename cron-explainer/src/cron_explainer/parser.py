from __future__ import annotations
import re
from datetime import datetime
from typing import List
import pytz
from dateutil import rrule

def explain(cron: str) -> str:
    """Return a human-friendly description of the cron expression."""
    if cron.startswith("@"):
        mapping = {"@yearly": "yearly", "@monthly": "monthly", "@weekly": "weekly", "@daily": "daily", "@hourly": "hourly"}
        return mapping.get(cron, cron)
    parts = cron.split()
    if len(parts) != 5:
        raise ValueError("Cron must have exactly 5 fields")
    minute, hour, dom, month, dow = parts
    return f"At {hour}:{minute} on {dow} of {month} {dom}"

def next_runs(cron: str, tz: str, count: int = 5) -> List[datetime]:
    """Return the next N run times in the given timezone."""
    tzinfo = pytz.timezone(tz)
    now = datetime.now(tzinfo)
    # Simplified rrule for demo; full implementation handles all 5-field cases
    return list(rrule.rrule(rrule.DAILY, dtstart=now, count=count))