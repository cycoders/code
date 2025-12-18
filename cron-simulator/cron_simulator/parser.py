import yaml
from pathlib import Path
from typing import List

from cron_simulator.models import Job


def parse_jobs(config_path: str | Path) -> List[Job]:
    """Parse jobs from YAML config file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    jobs = []
    for jdata in data.get("jobs", []):
        duration = jdata.get("duration", 60)
        jobs.append(Job(
            name=jdata["name"],
            cron=jdata["cron"],
            duration=duration,
        ))
    return jobs


def parse_datetime(dt_str: str, tz_name: str = "UTC") -> datetime:
    """Parse ISO-like datetime string with TZ."""
    from zoneinfo import ZoneInfo
    from datetime import datetime
    dt = datetime.fromisoformat(dt_str.replace(" ", "T"))
    return dt.replace(tzinfo=ZoneInfo(tz_name))