import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from .models import Snippet


class SnippetDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        )
        self._create_tables()

    def _create_tables(self):
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                language TEXT DEFAULT 'text',
                tags TEXT DEFAULT '',
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    @contextmanager
    def get_cursor(self):
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def _row_to_snippet(self, row: tuple) -> Snippet:
        return Snippet.from_db_row(row)

    def add(self, snippet: Snippet) -> int:
        snippet.created_at = snippet.updated_at = datetime.now()
        with self.get_cursor() as cur:
            cur.execute(
                "INSERT INTO snippets (title, language, tags, content) VALUES (?, ?, ?, ?)",
                (snippet.title, snippet.language, ",".join(snippet.tags), snippet.content),
            )
            sid = cur.lastrowid
        snippet.id = sid
        return sid

    def get(self, snippet_id: int) -> Optional[Snippet]:
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
            row = cur.fetchone()
            return self._row_to_snippet(row) if row else None

    def update(self, snippet: Snippet) -> None:
        snippet.updated_at = datetime.now()
        with self.get_cursor() as cur:
            cur.execute(
                """UPDATE snippets SET title=?, language=?, tags=?, content=?, updated_at=?
                   WHERE id=?""",
                (
                    snippet.title,
                    snippet.language,
                    ",".join(snippet.tags),
                    snippet.content,
                    snippet.updated_at,
                    snippet.id,
                ),
            )

    def delete(self, snippet_id: int) -> bool:
        with self.get_cursor() as cur:
            cur.execute("DELETE FROM snippets WHERE id=?", (snippet_id,))
            return cur.rowcount > 0

    def list_all(self, limit: Optional[int] = None) -> List[Snippet]:
        query = "SELECT * FROM snippets ORDER BY updated_at DESC"
        params = []
        if limit:
            query += " LIMIT ?"
            params = [limit]
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return [self._row_to_snippet(row) for row in cur.fetchall()]

    def search(self, query: str, limit: Optional[int] = None) -> List[Snippet]:
        all_snippets = self.list_all()
        if not query:
            return all_snippets[:limit] if limit else all_snippets
        from .search import fuzzy_search  # late import

        return fuzzy_search(all_snippets, query, limit=limit)
