from typing import Any, Dict, List
import psycopg2
from psycopg2 import OperationalError
from dbferry.core.adapters.base import BaseAdapter


class PostgresAdapter(BaseAdapter):
    """Adapter for Postgres Database"""

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port or 5432,
                dbname=self.config.database,
                user=self.config.user,
                password=self.config.password,
                sslmode=self.config.sslmode or "prefer",
            )
            return self.conn
        except OperationalError as e:
            raise ConnectionError(f"Postgres connection failed: {e}")

    def test_connection(self) -> bool:
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        self.close()
        return True

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

    def list_tables(self) -> List[str]:
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
        """
        cur = self.conn.cursor()
        cur.execute(query)
        tables = [r[0] for r in cur.fetchall()]
        cur.close()
        return tables

    def fetch_rows(self, table_name: str, limit: int = 1000) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM "{table_name}" LIMIT {limit};')
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        return rows

    def insert_rows(self, table_name: str, rows: list[dict]):
        if not rows:
            return
        cur = self.conn.cursor()
        columns = rows[0].keys()
        values = [[row[col] for col in columns] for row in rows]
        placeholders = ", ".join(["%s"] * len(columns))
        sql = (
            f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders})'
        )
        cur.executemany(sql, values)
        self.conn.commit()
        cur.close()
