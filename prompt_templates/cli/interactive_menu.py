"""
Interactive Inquirer-based menu for the Prompt Template CLI.
"""

import platform
import os
import time
import sys

from InquirerPy import inquirer
from typing import Dict
from rich.console import Console
from .template_manager import TemplateManager
from .clipboard import ClipboardManager
from .renderer import Renderer



def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if platform.system() == "Windows" else "clear")


class InteractiveMenu:
    """
    Handles the interactive menu flow using InquirerPy.
    """

    def __init__(self, template_manager: TemplateManager, args):
        self.template_manager = template_manager
        self.console: Console = template_manager.console
        self.clipboard = ClipboardManager(self.console)
        self.args = args  # Store CLI args for later use

    def run(self):
        """Main loop for the interactive menu."""
        while True:
            clear_screen()
            main_choice = inquirer.select(
                message="Main Menu - Choose an option:",
                choices=[
                    {"name": "Select a category", "value": "category"},
                    {"name": "Search for templates", "value": "search"},
                    {"name": "Exit", "value": "exit"},
                ],
            ).execute()

            if main_choice == "exit":
                self.console.print("[bold red]Exiting...[/bold red]")
                return

            if main_choice == "category":
                self._handle_category_selection()
            elif main_choice == "search":
                self._handle_search()

    def _handle_category_selection(self):
        """Menu flow for selecting a category and template."""
        clear_screen()
        category = inquirer.select(
            message="Select a category (or return):",
            choices=self.template_manager.list_categories() + ["Return to main menu"],
        ).execute()
        if category == "Return to main menu":
            return

        clear_screen()
        template_choice = inquirer.select(
            message="Select a template (or return):",
            choices=self.template_manager.list_templates_with_preview(category) + [{"name": "Return to main menu", "value": None}],
        ).execute()
        if template_choice is None:
            return

        self._display_template(*template_choice)

    def _handle_search(self):
        """Menu flow for searching templates by keyword."""
        clear_screen()
        search_term = inquirer.text(message="Enter search term:").execute()
        matches = self.template_manager.search_templates(search_term)
        if not matches:
            self.console.print(f"[bold red]No templates found for '{search_term}'.[/bold red]")
            return

        clear_screen()
        template_choice = inquirer.select(
            message="Search results:",
            choices=self.template_manager.list_templates_with_preview(file_paths=matches) + [{"name": "Return to main menu", "value": None}],
        ).execute()
        if template_choice is None:
            return

        self._display_template(*template_choice)

    def _display_template(self, category: str, template: str):
        """Loads, renders, and displays a selected template."""
        data, raw_yaml = self.template_manager.load_template(category, template)
        context = self._collect_context()

        # Use Renderer for Jinja2 rendering
        rendered_prompt = Renderer.render(data.get("style_prompt", ""), context)
        rendered_yaml = Renderer.render(raw_yaml, context)

        clear_screen()
        self.console.print("\n[bold yellow]Template Preview:[/bold yellow]")
        self.console.print(f"[bold cyan]name:[/bold cyan] {data.get('prompt_name', '').strip()}")
        self.console.print(f"[bold cyan]description:[/bold cyan] {data.get('description', '').strip()}")
        self.console.print(f"[bold cyan]prompt_content:[/bold cyan] {rendered_prompt.strip()}")

        for key, value in data.items():
            if key not in ["prompt_name", "description", "style_prompt"]:
                self.console.print(f"[bold cyan]{key}:[/bold cyan] {value}")

        if context:
            applied = ", ".join(f"{k}={v}" for k, v in context.items())
            self.console.print(f"\n[bold magenta]Applied Variables:[/bold magenta] {applied}")

        if inquirer.confirm(message="Copy full YAML to clipboard?", default=True).execute():
            self.clipboard.copy(rendered_yaml, "Copied full YAML to clipboard!")
            # Pause to allow user to see the message
            time.sleep(1.5)

        # Give the user the option to return to the main menu or exit
        choice = inquirer.select(
            message="What would you like to do?",
            choices=["Return to the main menu", "Exit"],
        ).execute()

        if choice == "Exit":
            self.console.print("[bold red]Exiting...[/bold red]")
            sys.exit(0)
        # If "Return to the main menu", just return to loop
        return
        
    def _collect_context(self) -> Dict[str, str]:
        """Collect context variables from CLI args only (no interactive prompts)."""
        context = {}
        if self.args.set:
            for kv in self.args.set:
                if "=" in kv:
                    key, value = kv.split("=", 1)
                    context[key] = value
        return context
