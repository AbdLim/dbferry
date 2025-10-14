from dbferry.core.console import Printer as p
from dbferry.core.config import MigrationConfig
from dbferry.core.connection import ConnectionManager
from dbferry.core.schema import TableSchema


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

            enums = self.source.list_enum_types()
            if enums:
                p.info("Recreating ENUM types on target...")
                for enum in enums:
                    try:
                        self.target.create_enum(enum)
                        p.success(f"Created ENUM: {enum.name}")
                    except Exception as e:
                        p.warn(f"Skipping {enum.name} (maybe exists): {e}")

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

            tables = [
                self.source.get_table_schema(name) for name in self.source.list_tables()
            ]
            order = resolve_table_order(tables=tables)

            for table in order:
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
            schema = self.source.get_table_schema(table)
            self.target.create_table(schema)
            p.success(f"Created table {table} on target (if not exists).")

            rows = self.source.fetch_rows(table_name=table, limit=1000)
            if not rows:
                p.warn(f"No rows found in {table}. Skipping.")
                return
            p.info(f"Fetched {len(rows)} rows in table {table}.")
            self.target.insert_rows(table_name=table, rows=rows)
            p.success(f"Migrated {len(rows)} rows for table {table}.")
        except Exception as e:
            p.error(f"Failed to migrate to table {table} :{e}")


import networkx as nx


def resolve_table_order(tables: list[TableSchema]):
    g = nx.DiGraph()
    for t in tables:
        g.add_node(t.name)
        for fk in t.foreign_keys or []:
            g.add_edge(fk.ref_table, t.name)
    return list(nx.topological_sort(g))
