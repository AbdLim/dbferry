# Registry of adapters
from dbferry.core.console import Printer as p
from dbferry.core.adapters.postgres import PostgresAdapter
from dbferry.core.config import DBConfig, MigrationConfig


ADAPTERS = {"postgres": PostgresAdapter}


class ConnectionManager:

    @staticmethod
    def get_adapter(db_cfg: DBConfig):
        db_type = db_cfg.type.lower()
        adapter_cls = ADAPTERS.get(db_type)
        if not adapter_cls:
            raise ValueError(f"Unsupported database type: {db_type}")
        return adapter_cls(db_cfg)

    @staticmethod
    def test_all(cfg: MigrationConfig):
        """Test both source and target connections."""
        p.info("Testing database connectivity...")

        for label, db_cfg in [("source", cfg.source), ("target", cfg.target)]:
            try:
                adapter = ConnectionManager.get_adapter(db_cfg)
                adapter.test_connection()
                p.success(f"{label.title()} ({db_cfg.type}) connection successful.")
            except Exception as e:
                p.error(f"{label.title()} ({db_cfg.type}) connection failed: {e}")

        p.info("[green]✅ Connectivity check complete[/green]")
