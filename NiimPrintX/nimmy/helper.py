import os
from rich.console import Console

# Check environment variable to determine ANSI color support
no_color = os.getenv("NO_COLOR") is not None

# Create a console object with or without color support
console = Console(color_system=None if no_color else "auto")


def print_success(message):
    """Prints a message indicating success in green color."""
    console.print(f"[bold green]{message}[/bold green] ")


def print_error(message):
    """Prints a message indicating an error in red color."""
    console.print(f"[bold red]{message}[/bold red]", style="bold red")


def print_info(message):
    """Prints an informational message in blue color."""
    console.print(f"[bold blue]{message}[/bold blue]", style="bold blue")
