"""
Clipboard utility for the Prompt Template CLI.
"""

import pyperclip
from rich.console import Console


class ClipboardManager:
    """
    Handles copying text content to the system clipboard.
    """

    def __init__(self, console: Console):
        self.console = console

    def copy(self, content: str, message: str = "Copied to clipboard!"):
        """
        Copy the given content to the clipboard and print a confirmation message.
        """
        pyperclip.copy(content)
        self.console.print(f"[bold green]{message}[/bold green]")