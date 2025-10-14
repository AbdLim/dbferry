from typing import List
import psycopg2
from psycopg2 import OperationalError
from dbferry.core.adapters.base import BaseAdapter


class PostgresAdapter(BaseAdapter):
    """Adapter for Postgres Database"""

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
