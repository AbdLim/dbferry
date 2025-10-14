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


if __name__ == "__main__":
    app()
