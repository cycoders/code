import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .models import CheckResult

class Storage:
    """SQLite storage for check history. JSON blobs for flexibility."""

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path or str(Path.home() / ".pulse-cli" / "history.db")).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    endpoint_name TEXT NOT NULL,
                    data TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_timestamp ON checks(timestamp);
                CREATE INDEX IF NOT EXISTS idx_endpoint ON checks(endpoint_name);
                """
            )
            conn.commit()

    def store(self, result: CheckResult) -> None:
        """Store result with endpoint_name in data."""
        data = result.model_dump()
        data["endpoint_name"] = result.endpoint_name
        data_json = json.dumps(data)
        timestamp_str = result.timestamp.isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO checks (timestamp, endpoint_name, data) VALUES (?, ?, ?)",
                (timestamp_str, result.endpoint_name, data_json),
            )
            conn.commit()

    def get_checks(
        self, endpoint_name: Optional[str] = None, limit: int = 100, days: Optional[int] = None
    ) -> List[CheckResult]:
        """Query checks, newest first."""
        params = []
        where_clauses = []
        if endpoint_name:
            where_clauses.append("endpoint_name = ?")
            params.append(endpoint_name)
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where_clauses.append("timestamp >= ?")
            params.append(cutoff)
        where = " AND ".join(where_clauses)
        where_str = f"WHERE {where}" if where else ""
        query = f"""
            SELECT data FROM checks {where_str}
            ORDER BY timestamp DESC LIMIT ?
        """
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(query, params)
            rows = cur.fetchall()
        return [CheckResult.model_validate_json(row[0]) for row in rows]

    def get_latest_per_endpoint(self) -> List[CheckResult]:
        """Get latest check per endpoint."""
        query = """
            SELECT c.data FROM checks c
            INNER JOIN (
                SELECT endpoint_name, MAX(timestamp) as max_ts
                FROM checks GROUP BY endpoint_name
            ) latest ON c.endpoint_name = latest.endpoint_name AND c.timestamp = latest.max_ts
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(query)
            rows = cur.fetchall()
        return [CheckResult.model_validate_json(row[0]) for row in rows]