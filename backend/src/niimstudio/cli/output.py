import os

from rich.console import Console

console = Console(color_system=None if os.getenv("NO_COLOR") is not None else "auto")


def print_success(message: object) -> None:
    console.print(f"[bold green]{message}[/bold green]")


def print_error(message: object) -> None:
    console.print(f"[bold red]{message}[/bold red]")


def print_info(message: object) -> None:
    console.print(f"[bold blue]{message}[/bold blue]")
