from typing import Any, Dict, List
import pymysql
from dbferry.core.adapters.base import BaseAdapter
from dbferry.core.schema import (
    ColumnSchema,
    TableSchema,
    UniqueKeySchema,
    ForeignKeySchema,
)


class MySQLAdapter(BaseAdapter):
    """Adapter for MySQL Database"""

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.config.host,
                port=self.config.port or 3306,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
            
            # Try to disable strict PK requirement for this session if possible
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SET SESSION sql_require_primary_key = 0;")
            except Exception:
                pass # Ignore if permission denied or not supported

            return self.conn
        except pymysql.MySQLError as e:
            raise ConnectionError(f"MySQL connection failed: {e}")

    def test_connection(self) -> bool:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        self.close()
        return True

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

    def get_table_schema(self, table_name: str) -> TableSchema:
        with self.conn.cursor() as cur:
            # Columns
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s;
                """,
                (self.config.database, table_name),
            )

            columns = []
            for row in cur.fetchall():
                columns.append(
                    ColumnSchema(
                        name=row["column_name"],
                        type=row["data_type"],
                        nullable=(row["is_nullable"] == "YES"),
                        default=row["column_default"],
                    )
                )

            # Primary key
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = %s AND table_name = %s AND constraint_name = 'PRIMARY';
                """,
                (self.config.database, table_name),
            )
            primary_key = [row["column_name"] for row in cur.fetchall()]

            # Unique keys (excluding PK)
            cur.execute(
                """
                SELECT constraint_name, column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = %s AND table_name = %s
                AND constraint_name != 'PRIMARY'
                AND constraint_name IN (
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE constraint_type = 'UNIQUE'
                )
                ORDER BY constraint_name, ordinal_position;
                """,
                (self.config.database, table_name),
            )
            
            unique_map = {}
            for row in cur.fetchall():
                unique_map.setdefault(row["constraint_name"], []).append(row["column_name"])
            
            unique_keys = [UniqueKeySchema(columns=cols) for cols in unique_map.values()]

            # Foreign keys
            cur.execute(
                """
                SELECT column_name, referenced_table_name, referenced_column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = %s AND table_name = %s
                AND referenced_table_name IS NOT NULL;
                """,
                (self.config.database, table_name),
            )
            foreign_keys = [
                ForeignKeySchema(
                    column=row["column_name"],
                    ref_table=row["referenced_table_name"],
                    ref_column=row["referenced_column_name"],
                )
                for row in cur.fetchall()
            ]

            return TableSchema(
                name=table_name,
                columns=columns,
                primary_key=primary_key,
                unique_keys=unique_keys,
                foreign_keys=foreign_keys,
            )

    def _map_type(self, col_type: str) -> str:
        """Map Postgres/Generic types to MySQL types."""
        col_type = col_type.lower()
        if "character varying" in col_type:
            return "VARCHAR(255)"
        if "text" in col_type:
            return "TEXT"
        if "timestamp" in col_type:
            return "DATETIME"
        if "boolean" in col_type:
            return "TINYINT(1)"
        if "integer" in col_type:
            return "INT"
        
        # Fallback for Enums and custom types
        return "VARCHAR(255)"

    def create_table(self, schema: TableSchema):
        cols_sql = []
        
        for col in schema.columns:
            mysql_type = self._map_type(col.type)
            col_sql = f"`{col.name}` {mysql_type}"
            
            is_auto_increment = False
            col_default = col.default

            # Handle defaults
            if col_default:
                if "nextval" in col_default:
                    is_auto_increment = True
                    col_default = None
                elif "true" == col_default.lower():
                    col_default = "1"
                elif "false" == col_default.lower():
                    col_default = "0"
                elif "::" in col_default:
                    # Strip postgres casts like 'now()::timestamp'
                    col_default = col_default.split("::")[0]

            if not col.nullable:
                col_sql += " NOT NULL"
            
            if is_auto_increment:
                col_sql += " AUTO_INCREMENT"
            elif col_default:
                col_sql += f" DEFAULT {col_default}"
            
            cols_sql.append(col_sql)

        if schema.primary_key:
            pk_cols = ", ".join(f"`{col}`" for col in schema.primary_key)
            cols_sql.append(f"PRIMARY KEY ({pk_cols})")

        sql = f"CREATE TABLE IF NOT EXISTS `{schema.name}` ({', '.join(cols_sql)});"
        
        with self.conn.cursor() as cur:
            try:
                cur.execute(sql)
            except Exception as e:
                raise Exception(f"Failed to create table {schema.name}: {e}")

    def list_tables(self) -> List[str]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s AND table_type = 'BASE TABLE';
                """,
                (self.config.database,),
            )
            return [row["table_name"] for row in cur.fetchall()]

    def fetch_rows(self, table_name: str, limit: int = 1000) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{table_name}` LIMIT {limit};")
            return cur.fetchall()

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        
        columns = list(rows[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        cols_str = ", ".join(f"`{c}`" for c in columns)
        
        values = [[row[col] for col in columns] for row in rows]
        
        sql = f"INSERT INTO `{table_name}` ({cols_str}) VALUES ({placeholders})"
        
        with self.conn.cursor() as cur:
            cur.executemany(sql, values)

    def count_rows(self, table_name: str) -> int:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as count FROM `{table_name}`;")
            return cur.fetchone()["count"]
