from dbferry.core.console import Printer as p
from dbferry.core.config import MigrationConfig
from dbferry.core.connection import ConnectionManager


class MigrationManager:

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.conn_mgr = ConnectionManager()

        self.source = self.conn_mgr.get_adapter(self.config.source)
        self.target = self.conn_mgr.get_adapter(self.config.target)

    def run(self):
        p.panel(title="Migration", message="Starting migration process...")

        try:
            self.source.connect()
            self.target.connect()
            p.success("DB Connections success")

            # Determine which tables to migrate
            if self.config.options.tables == ["*"]:
                tables = self.source.list_tables()
                p.info(f"Discovered {len(tables)} tables from source database.")
            else:
                tables = self.config.options.tables or []
                p.info(f"Using specified tables from config: {', '.join(tables)}")

            if not tables:
                p.warn("No tables found or specified. Exiting migration.")
                return

            for table in tables:
                self.migrate_table(table)

            p.panel(
                title="Migration",
                message="Migration completed succesfully!",
                style="green",
            )
        except Exception as e:
            p.error(f"Migration failed: {e}")
        finally:
            self.source.close()
            self.target.close()

    def migrate_table(self, table: str):
        p.info(f"Migrating table [bold]{table}[/bold]..")

        try:
            rows = self.source.fetch_rows(table_name=table, limit=1000)
            if not rows:
                p.warn(f"No rows found in {table}. Skipping.")
                return
            p.info(f"Fetched {len(rows)} rows in table {table}.")
            self.target.insert_rows(table_name=table, rows=rows)
            p.success(f"Migrated {len(rows)} rows for table {table}.")
        except Exception as e:
            p.error(f"Failed to migrate to table {table} :{e}")
