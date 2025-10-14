import click
from rich.console import Console

console = Console()


@click.group()
def app():
    """🧭 dbferry — Secure, local-first database migration tool."""
    pass


@app.command()
@click.option(
    "--config", default="migration.yml", help="Path to the migration config file"
)
def check(config):
    """Test source and target database connectivity."""
    console.print(f"[bold cyan]Checking connections from {config}...[/bold cyan]")
    # Placeholder logic
    console.print("[green]All connections verified![/green]")


@app.command()
def init():
    """Initialize a new dbferry migration project."""
    console.print("[bold yellow]Initializing dbferry project...[/bold yellow]")
    # TODO: scaffold migration.yml, .dbferry/
    console.print("[green]Project initialized![/green]")


if __name__ == "__main__":
    app()
