import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import appdirs

class HistoryManager:
    def __init__(self) -> None:
        self.data_dir = Path(appdirs.user_data_dir("graphql-tester-cli", "cycoders"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "history.db"
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    query TEXT NOT NULL,
                    variables TEXT,
                    result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def save(
        self,
        endpoint: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        vars_json = json.dumps(variables) if variables else None
        res_json = json.dumps(result) if result else None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO queries (endpoint, query, variables, result) VALUES (?, ?, ?, ?)",
                (endpoint, query, vars_json, res_json),
            )
            conn.commit()

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, endpoint, query, timestamp FROM queries ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "endpoint": row[1][:40] + "..." if len(row[1]) > 40 else row[1],
                "query": row[2][:60] + "..." if len(row[2]) > 60 else row[2],
                "timestamp": row[3],
            }
            for row in rows
        ]

    def get(self, query_id: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT endpoint, query, variables, result, timestamp FROM queries WHERE id = ?",
                (query_id,),
            )
            row = cursor.fetchone()
        if row:
            return {
                "id": query_id,
                "endpoint": row[0],
                "query": row[1],
                "variables": json.loads(row[2]) if row[2] else {},
                "result": json.loads(row[3]) if row[3] else {},
                "timestamp": row[4],
            }
        return None
