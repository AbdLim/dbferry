import click
from pathlib import Path
import yaml

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
        },
        "target": {
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "target_db",
            "user": "username",
            "password": "password",
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
        cfg = yaml.safe_load(path.read_text())
        source, target = cfg.get("source"), cfg.get("target")
        p.panel(
            message=f"[bold]Source:[/bold] {source['type']} → [bold]Target:[/bold] {target['type']}",
            title="Connections",
            style="blue",
        )
        p.success("Configuration loaded successfully.")
        p.warn("Actual DB connectivity tests will be added later.")
    except Exception as e:
        p.error(f"Error reading config: {e}")


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def migrate(config):
    """
    Run a mock migration based on the provided configuration.
    """
    p.info(f"Starting migration using {config}...")
    # TODO: Replace this with real migration logic in dbferry/core/migrate.py
    p.success("Migration completed successfully (simulated).")


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def verify(config):
    """
    Verify that the target database matches the source after migration.
    """
    p.info(f"Running post-migration verification using {config}...")
    # TODO: Replace this with real data validation logic
    rows = [
        ["users", "100%", "[green]OK[/green]"],
        ["orders", "99.8%", "[yellow]Minor diff[/yellow]"],
    ]
    p.table("Verification Summary", ["Table", "Rows Matched", "Status"], rows)
    p.success("Verification completed (mock).")


if __name__ == "__main__":
    app()
