#!/usr/bin/env python3
"""
Main entry point for the Prompt Template CLI.
"""

import os
from .interactive_menu import InteractiveMenu
from .arguments import parse_args
from .template_manager import TemplateManager
from rich.console import Console


def main():
    """CLI entry point."""
    base_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    console = Console()
    template_manager = TemplateManager(base_dir=base_dir, console=console)
    args = parse_args()

    # Default to interactive if no other args
    if not any([args.category, args.template, args.set, args.interactive]):
        args.interactive = True

    if args.interactive:
        InteractiveMenu(template_manager, args).run()
    else:
        console.print("[bold red]Non-interactive mode not implemented yet.[/bold red]")


if __name__ == "__main__":
    main()
