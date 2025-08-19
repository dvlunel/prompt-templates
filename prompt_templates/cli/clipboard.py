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
        Copy the given content to the clipboard, wrapped in a template, and print a confirmation message.
        """
        wrapped_content = "Use this prompt template as instructions:\n\n" f"{content}"
        pyperclip.copy(wrapped_content)
        self.console.print(f"[bold green]{message}[/bold green]")
