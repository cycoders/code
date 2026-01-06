import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = "emails.db"

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sender TEXT NOT NULL,
    recipients TEXT NOT NULL,
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    headers TEXT NOT NULL
)
"""

SQL_LIST = """
SELECT id, received_at, sender, recipients, subject 
FROM emails %s
ORDER BY id DESC LIMIT ?
"""

SQL_GET = "SELECT * FROM emails WHERE id = ?"
SQL_DELETE = "DELETE FROM emails WHERE id = ?"
SQL_CLEAR = "DELETE FROM emails"


def get_db_path(data_dir: Path) -> Path:
    return data_dir / DB_PATH


def init_db(data_dir: Path) -> None:
    db_path = get_db_path(data_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(SQL_CREATE)
        conn.commit()


def save_email(data_dir: Path, email_dict: Dict[str, Any]) -> None:
    init_db(data_dir)
    db_path = get_db_path(data_dir)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO emails (sender, recipients, subject, body_text, body_html, headers)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                email_dict["sender"],
                json.dumps(email_dict["recipients"]),
                email_dict["subject"],
                email_dict["body_text"],
                email_dict["body_html"],
                json.dumps(email_dict["headers"]),
            ),
        )
        conn.commit()


def list_email_summaries(
    data_dir: Path, limit: int = 10, sender_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    init_db(data_dir)
    db_path = get_db_path(data_dir)
    where_clause = "WHERE sender LIKE ?" if sender_filter else ""
    params = [(f"%{sender_filter}%", limit)] if sender_filter else [limit]
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(SQL_LIST % where_clause, params)
        rows = cur.fetchall()
    summaries = []
    for row in rows:
        recips = json.loads(row["recipients"] or "[]")
        summaries.append(
            {
                "id": row["id"],
                "received_at": row["received_at"],
                "sender": row["sender"],
                "recipients_count": len(recips),
                "subject": row["subject"],
            }
        )
    return summaries


def get_email(data_dir: Path, id_: int) -> Optional[Dict[str, Any]]:
    init_db(data_dir)
    db_path = get_db_path(data_dir)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(SQL_GET, (id_,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "received_at": row["received_at"],
            "sender": row["sender"],
            "recipients": json.loads(row["recipients"]),
            "subject": row["subject"],
            "body_text": row["body_text"],
            "body_html": row["body_html"],
            "headers": json.loads(row["headers"]),
        }


def delete_email(data_dir: Path, id_: int) -> bool:
    init_db(data_dir)
    db_path = get_db_path(data_dir)
    with sqlite3.connect(db_path) as conn:
        res = conn.execute(SQL_DELETE, (id_,)).rowcount
        conn.commit()
        return res > 0


def clear_emails(data_dir: Path) -> None:
    init_db(data_dir)
    db_path = get_db_path(data_dir)
    with sqlite3.connect(db_path) as conn:
        conn.execute(SQL_CLEAR)
        conn.commit()