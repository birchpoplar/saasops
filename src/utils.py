from src import classes
from rich.console import Console
from rich.text import Text

# Utility functions

def print_status(console: Console, message: str, style: classes.MessageStyle) -> None:
    """Print a status message with the specified style."""
    console.print(Text(message, style=style.value))
