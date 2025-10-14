from typing import Any, Dict, List
import psycopg2
from psycopg2 import OperationalError
from dbferry.core.adapters.base import BaseAdapter
from dbferry.core.schema import (
    ColumnSchema,
    EnumType,
    ForeignKeySchema,
    TableSchema,
    UniqueKeySchema,
)


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
            self.conn.autocommit = True
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

    def get_table_schema(self, table_name: str) -> TableSchema:
        cur = self.conn.cursor()

        # Columns
        cur.execute(
            """
            SELECT column_name, data_type, udt_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s;
            """,
            (table_name,),
        )

        columns = []
        for n, t, udt, nn, d in cur.fetchall():
            # Handle enums or custom types
            if t == "USER-DEFINED":
                t = udt
            columns.append(
                ColumnSchema(name=n, type=t, nullable=(nn == "YES"), default=d)
            )

        # Primary key
        cur.execute(
            """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary;
            """,
            (table_name,),
        )
        primary_key = [r[0] for r in cur.fetchall()]

        # Unique keys
        cur.execute(
            """
            SELECT
                i.relname AS index_name,
                ARRAY_AGG(a.attname ORDER BY a.attnum) AS column_names
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = %s AND ix.indisunique AND NOT ix.indisprimary
            GROUP BY i.relname;
            """,
            (table_name,),
        )
        unique_keys = [
            UniqueKeySchema(columns=list(cols)) for _, cols in cur.fetchall()
        ]

        # Foreign keys
        cur.execute(
            """
            SELECT
                kcu.column_name,
                ccu.table_name AS ref_table,
                ccu.column_name AS ref_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
            """,
            (table_name,),
        )
        foreign_keys = [
            ForeignKeySchema(column=c, ref_table=rt, ref_column=rc)
            for c, rt, rc in cur.fetchall()
        ]

        cur.close()
        return TableSchema(
            name=table_name,
            columns=columns,
            primary_key=primary_key,
            unique_keys=unique_keys,
            foreign_keys=foreign_keys,
        )

    def create_table(self, schema: TableSchema):
        cols_sql = []
        for col in schema.columns:
            col_sql = f'"{col.name}" {col.type}'
            if not col.nullable:
                col_sql += " NOT NULL"
            if col.default:
                col_sql += f" DEFAULT {col.default}"
            cols_sql.append(col_sql)
        sql = f'CREATE TABLE IF NOT EXISTS "{schema.name}" ({", ".join(cols_sql)});'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()

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

    def list_enum_types(self) -> list[EnumType]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT t.typname AS enum_type, e.enumlabel AS enum_label
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname = 'public'
            ORDER BY t.typname, e.enumlabel;
        """
        )
        results = {}
        for enum_type, label in cur.fetchall():
            results.setdefault(enum_type, []).append(label)
        cur.close()
        return [EnumType(name=k, values=v) for k, v in results.items()]

    def create_enum(self, enum: EnumType):
        cur = self.conn.cursor()
        values = ", ".join(f"'{v}'" for v in enum.values)
        cur.execute(f"CREATE TYPE {enum.name} AS ENUM ({values});")
        cur.close()

    def count_rows(self, table_name: str) -> int:
        """Return row count from the specified table."""
        with self.conn.cursor() as cur:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                return cur.fetchone()[0]
            except Exception as e:
                raise RuntimeError(f"Failed to count rows in {table_name}: {e}")
