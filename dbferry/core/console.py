from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Printer:
    """Unified console helper for dbferry output."""

    @staticmethod
    def info(message: str):
        console.print(f"[cyan]{message}[/cyan]")

    @staticmethod
    def success(message: str):
        console.print(f"[green]{message}[/green]")

    @staticmethod
    def warn(message: str):
        console.print(f"[yellow]{message}[/yellow]")

    @staticmethod
    def error(message: str):
        console.print(f"[red]{message}[/red]")

    @staticmethod
    def panel(message: str, title: str = "", style: str = "blue"):
        console.print(Panel.fit(message, title=title, border_style=style))

    @staticmethod
    def table(title: str, columns: list[str], rows: list[list[str]]):
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        console.print(table)
