import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import yaml

console = Console()


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
        console.print("[yellow]migration.yml already exists.[/yellow]")
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

    console.print(
        Panel.fit(
            "[green]✅ Created sample migration.yml[/green]\nEdit it with your database credentials before running `dbferry check`.",
            title="Initialization Complete",
            border_style="green",
        )
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
        console.print(f"[red]❌ Config file not found: {path}[/red]")
        return

    console.print("[cyan]Reading configuration...[/cyan]")
    try:
        cfg = yaml.safe_load(path.read_text())
        source, target = cfg.get("source"), cfg.get("target")
        console.print(
            Panel(
                f"[bold]Source:[/bold] {source['type']} → [bold]Target:[/bold] {target['type']}",
                title="Connections",
                border_style="blue",
            )
        )
        console.print("[green]✅ Configuration loaded successfully.[/green]")
        console.print(
            "[yellow]⚠️ Actual DB connectivity tests will be added later.[/yellow]"
        )
    except Exception as e:
        console.print(f"[red]Error reading config: {e}[/red]")


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def migrate(config):
    """
    Run a mock migration based on the provided configuration.
    """
    console.print(f"[cyan]Starting migration using {config}...[/cyan]")
    # TODO: Replace this with real migration logic in dbferry/core/migrate.py
    console.print("[green]✅ Migration completed successfully (simulated).[/green]")


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def verify(config):
    """
    Verify that the target database matches the source after migration.
    """
    console.print(f"[cyan]Running post-migration verification using {config}...[/cyan]")
    # TODO: Replace this with real data validation logic
    table = Table(title="Verification Summary")
    table.add_column("Table")
    table.add_column("Rows Matched", justify="center")
    table.add_column("Status", justify="center")
    table.add_row("users", "100%", "[green]OK[/green]")
    table.add_row("orders", "99.8%", "[yellow]Minor diff[/yellow]")
    console.print(table)
    console.print("[green]Verification completed (mock).[/green]")


if __name__ == "__main__":
    app()
