'''Timezone management utilities.'''

from datetime import datetime
from typing import List, Dict
import zoneinfo

DEFAULT_TZS: List[str] = [
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Australia/Sydney",
]

def search_timezones(query: str) -> List[str]:
    """Search available timezones by substring (case-insensitive)."""
    query_lower = query.lower()
    return [
        tz
        for tz in sorted(zoneinfo.available_timezones())
        if query_lower in tz.lower()
    ]

def get_all_timezones() -> List[str]:
    """Return sorted list of all available timezones."""
    return sorted(zoneinfo.available_timezones())

def get_current_time(tz_name: str, utc_now: datetime) -> Dict[str, str]:
    """Get formatted time info for a timezone given UTC now."""
    try:
        tz = zoneinfo.ZoneInfo(tz_name)
        now_local = utc_now.astimezone(tz)
        offset_hours = now_local.utcoffset().total_seconds() / 3600
        offset_str = f"UTC{offset_hours:+.0f}"
        time_str = now_local.strftime("%H:%M")
        date_str = now_local.strftime("%Y-%m-%d %A")
        return {
            "name": tz_name,
            "offset": offset_str,
            "time": time_str,
            "date": date_str,
        }
    except ValueError:
        raise ValueError(f"Invalid timezone '{tz_name}'")