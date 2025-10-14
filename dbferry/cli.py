import click
from pathlib import Path
import yaml

from dbferry.core.config import ConfigLoader
from dbferry.core.console import Printer as p


@click.group()
def app():
    """🧭 dbferry — A secure, local-first database migration tool."""
    pass


@app.command()
def init():
    """
    Initialize a new dbferry migration configuration in the current directory.
    """
    config_path = Path("migration.yml")

    if config_path.exists():
        p.warn("migration.yml already exists.")
        return

    sample_config = {
        "source": {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "user": "username",
            "password": "password",
            "sslmode": "require",
        },
        "target": {
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "target_db",
            "user": "username",
            "password": "password",
            "sslmode": "require",
        },
        "options": {
            "tables": ["*"],
            "verify_after_migration": True,
        },
    }

    with open(config_path, "w") as f:
        yaml.dump(sample_config, f, sort_keys=False)

    p.panel(
        message="[green]✅ Created sample migration.yml[/green]\n"
        "Edit it with your database credentials before running `dbferry check`.",
        title="Initialization Complete",
        style="green",
    )


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def check(config):
    """
    Verify connectivity to the source and target databases.
    """
    path = Path(config)
    if not path.exists():
        p.error(f"Config file not found: {path}")
        return

    p.info("Reading configuration...")
    try:
        cfg = ConfigLoader.load(path)
        source, target = cfg.source, cfg.target
        p.panel(
            message=f"[bold]Source:[/bold] {source.type} → [bold]Target:[/bold] {target.type}",
            title="Connections",
            style="blue",
        )
        p.success("Configuration loaded successfully.")

        #
        from dbferry.core.connection import ConnectionManager

        conn_mgr = ConnectionManager()
        results = {}

        for name, db_cfg in [(("source"), source), (("target"), target)]:
            try:
                p.info(f"Connecting to {name} database ({db_cfg.type})...")
                adapter = conn_mgr.get_adapter(db_cfg)
                adapter.connect()
                adapter.test_connection()
                results[name] = True
                p.success(f"{name.capitalize()} connection successful")
            except Exception as e:
                results[name] = False
                p.error(f"❌ {name.capitalize()} connection failed: {e}")

        # Summary
        if all(results.values()):
            p.panel(
                title="Success",
                style="green",
                message="All connections verified succesfully!",
            )
        else:
            p.panel("One or more connections failed.", title="Error", style="red")
    except Exception as e:
        p.error(f"Error reading config: {e}")


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
@click.option("--dry-run", is_flag=True, help="Simulate migration without writing data")
def migrate(config, dry_run):
    """
    Run a mock migration based on the provided configuration.
    """
    p.info(
        f"Starting migration using {config} {'(dry-run mode)' if dry_run else ''}..."
    )
    from dbferry.core.config import ConfigLoader
    from dbferry.core.migrate import MigrationManager

    p.info(f"Loading configuration from {config}...")
    path = Path(config)
    if not path.exists():
        p.error(f"Config file not found: {path}")
        return

    try:
        cfg = ConfigLoader.load(path)
        mgr = MigrationManager(config=cfg, dry_run=dry_run)
        mgr.run()
    except Exception as e:
        p.error(f"Migration failed: {e}")


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def verify(config):
    """
    Verify that the target database matches the source after migration.
    Compares row counts table-by-table and renders a summary.
    """
    from dbferry.core.connection import ConnectionManager
    from dbferry.core.config import ConfigLoader

    path = Path(config)
    if not path.exists():
        p.error(f"Config file not found: {path}")
        return

    p.info(f"Starting verification using {config}...")

    try:
        cfg = ConfigLoader.load(path)
        conn_mgr = ConnectionManager()

        source = conn_mgr.get_adapter(cfg.source)
        target = conn_mgr.get_adapter(cfg.target)

        source.connect()
        target.connect()

        tables = source.list_tables()
        if not tables:
            p.warn("No tables found in source database.")
            return

        p.info(f"Discovered {len(tables)} tables from source database.")

        rows = []
        for tbl in tables:
            try:
                src_count = source.count_rows(tbl)
                tgt_count = target.count_rows(tbl)

                if src_count == tgt_count:
                    status = "[green]✓ Match[/green]"
                else:
                    status = f"[yellow]⚠ Mismatch ({abs(src_count - tgt_count)} diff)[/yellow]"

                rows.append([tbl, str(src_count), str(tgt_count), status])
            except Exception as e:
                rows.append([tbl, "—", "—", f"[red]Error: {e}[/red]"])

        p.table(
            title="Verification Summary",
            columns=["Table", "Source Rows", "Target Rows", "Status"],
            rows=rows,
        )

        if all("Match" in r[-1] for r in rows):
            p.panel(
                "All tables verified successfully.", title="Verification", style="green"
            )
        else:
            p.panel(
                "Verification completed with mismatches or errors.",
                title="Verification",
                style="yellow",
            )

    except Exception as e:
        p.error(f"Verification failed: {e}")


if __name__ == "__main__":
    app()
