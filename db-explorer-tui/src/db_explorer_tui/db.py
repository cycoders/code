import databases
import sqlparse
from typing import List, Any, Dict, Tuple
from pathlib import Path


class DBManager:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.engine = dsn.split("://")[0].split("+")[0].lower()
        self._conn: databases.Database | None = None

    async def connect(self) -> None:
        """Connect to the database."""
        self._conn = await databases.connect(self.dsn)

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._conn:
            await self._conn.disconnect()

    async def execute(self, query: str) -> List[Dict[str, Any]]:
        """Execute query and return rows."""
        if not self._conn:
            raise RuntimeError("Not connected")
        # Format query for better errors
        formatted = sqlparse.format(query, reindent=True)
        return await self._conn.fetch_all(formatted)

    async def get_tables(self) -> List[str]:
        """Fetch table names engine-specifically."""
        if not self._conn:
            raise RuntimeError("Not connected")
        if self.engine == "sqlite":
            rows = await self._conn.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
            )
            return [row["name"] for row in rows]
        elif self.engine == "postgresql":
            rows = await self._conn.fetch_all(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = current_schema() AND table_type = 'BASE TABLE';",
            )
            return [row["table_name"] for row in rows]
        elif self.engine == "mysql":
            rows = await self._conn.fetch_all("SHOW TABLES;")
            return [list(row.values())[0] for row in rows]
        raise ValueError(f"Unsupported engine: {self.engine}")

    async def get_columns(self, table: str) -> List[str]:
        """Fetch column names for table."""
        if not self._conn:
            raise RuntimeError("Not connected")
        if self.engine == "sqlite":
            rows = await self._conn.fetch_all(f"PRAGMA table_info(`{table}`);")
            return [row["name"] for row in rows]
        elif self.engine == "postgresql":
            rows = await self._conn.fetch_all(
                "SELECT column_name FROM information_schema.columns "
                f"WHERE table_name = $1 AND table_schema = current_schema();",
                [table],
            )
            return [row["column_name"] for row in rows]
        elif self.engine == "mysql":
            rows = await self._conn.fetch_all(f"DESCRIBE `{table}`;")
            return [row["Field"] for row in rows]
        raise ValueError(f"Unsupported engine: {self.engine}")

    async def close(self) -> None:
        await self.disconnect()