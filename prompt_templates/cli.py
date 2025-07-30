#!/usr/bin/env python3
"""
Prompt Template CLI
-------------------

An object-oriented CLI for selecting and rendering YAML-based
prompt templates using Jinja2. Supports:
- Browsing categories and templates interactively (with nested folders).
- Passing variables via command-line arguments.
- Rendering templates with dynamic values.
- Copying the full YAML output to the clipboard.
"""

import platform
import os
import yaml
import pyperclip
import argparse
from typing import List, Tuple, Dict
from jinja2 import Template
from rich.console import Console
from InquirerPy import inquirer


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if platform.system() == "Windows" else "clear")


class PromptTemplateCLI:
    """
    A CLI tool for browsing and rendering YAML prompt templates.
    """

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.console = Console()

    def list_categories(self) -> List[str]:
        """
        List all available template categories (top-level folders).
        """
        return [
            d for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
        ]

    def list_templates_with_preview(self, category: str = None, file_paths: list = None) -> List[Dict[str, str]]:
        """
        List templates with name and description preview.
        Works for a specific category or a list of file paths (for search results).
        """
        templates = []
        files_to_process = []

        if file_paths:
            files_to_process = [(os.path.dirname(os.path.relpath(fp, self.base_dir)),
                                 os.path.basename(fp)) for fp in file_paths]
        elif category:
            category_path = os.path.join(self.base_dir, category)
            for root, _, files in os.walk(category_path):
                for f in files:
                    if f.endswith((".yaml", ".yml")):
                        rel_dir = os.path.relpath(root, self.base_dir)
                        files_to_process.append((rel_dir, f))

        for cat, filename in files_to_process:
            file_path = os.path.join(self.base_dir, cat, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    raw = file.read()
                    rendered_raw = Template(raw).render()
                    data = yaml.safe_load(rendered_raw) or {}
                except yaml.YAMLError:
                    data = {}
                name = data.get("prompt_name") or "Unnamed template"
                description = data.get("description") or "No description available"
                display = f"{cat}/{filename}\n  name: {name}\n  description: {description}"
                templates.append({"name": display, "value": (cat, filename)})
        return templates

    def load_template(self, category: str, rel_path: str) -> Tuple[Dict, str]:
        """
        Load a YAML template and its raw content by category and relative path.
        """
        file_path = os.path.join(self.base_dir, category, rel_path)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        if raw_content.startswith("---"):
            raw_content = raw_content.split("\n", 1)[1]
        return yaml.safe_load(raw_content), raw_content

    @staticmethod
    def render_template(content: str, context: Dict[str, str]) -> str:
        return Template(content).render(**context)

    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Prompt Template CLI")
        parser.add_argument("--category", help="Category (skip menu)")
        parser.add_argument("--template", help="Template relative path (skip menu)")
        parser.add_argument("--set", nargs="*", help="Set key=value pairs for template variables")
        return parser.parse_args()

    def interactive_menu(self) -> None:
        while True:  # Keep looping to allow returning to main menu
            clear_screen()
            # Main menu
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

            # Handle selecting a category
            if main_choice == "category":
                clear_screen()
                category = inquirer.select(
                    message="Select a category (or return):",
                    choices=self.list_categories() + ["Return to main menu"],
                ).execute()
                if category == "Return to main menu":
                    continue  # Go back to main menu

                clear_screen()
                template_choice = inquirer.select(
                    message="Select a template (or return):",
                    choices=self.list_templates_with_preview(category) + [{"name": "Return to main menu", "value": None}],
                ).execute()
                if template_choice is None:
                    continue  # Back to main menu
                category, template = template_choice

            # Handle searching templates
            elif main_choice == "search":
                clear_screen()
                search_term = inquirer.text(message="Enter search term:").execute()
                matches = self.search_templates(search_term)
                if not matches:
                    self.console.print(f"[bold red]No templates found for '{search_term}'.[/bold red]")
                    continue
                clear_screen()
                template_choice = inquirer.select(
                    message="Search results:",
                    choices=self.list_templates_with_preview(file_paths=matches) + [{"name": "Return to main menu", "value": None}],
                ).execute()
                if template_choice is None:
                    continue
                category, template = template_choice

            # Load and render template
            data, raw_yaml = self.load_template(category, template)
            context = self._collect_context()
            rendered_prompt = self.render_template(data.get("style_prompt", ""), context)
            rendered_yaml = self.render_template(raw_yaml, context)

            clear_screen()
            # Display preview
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
                pyperclip.copy(rendered_yaml)
                self.console.print("[bold green]Copied full YAML to clipboard![/bold green]")

    def _collect_context(self) -> Dict[str, str]:
        """Helper for parsing CLI args into context."""
        args = self.parse_args()
        context = {}
        if args.set:
            for kv in args.set:
                key, value = kv.split("=", 1)
                context[key] = value
        return context

    def search_templates(self, search_term: str) -> list:
        """Return a list of file paths for matching templates."""
        matches = []
        for root, _, files in os.walk(self.base_dir):
            for f in files:
                if f.endswith((".yaml", ".yml")):
                    full_path = os.path.join(root, f)
                    with open(full_path, "r", encoding="utf-8") as file:
                        data = yaml.safe_load(file)
                        if not isinstance(data, dict):
                            continue
                        desc = data.get("description", "").lower()
                        tags = [t.lower() for t in data.get("tags", [])] if isinstance(data.get("tags"), list) else []
                        filename = f.lower()
                        if (search_term.lower() in desc) or (search_term.lower() in tags) or (search_term.lower() in filename):
                            matches.append(full_path)
        return matches
    
    
def main() -> None:
    cli = PromptTemplateCLI(base_dir=os.path.join(os.path.dirname(__file__), "templates"))
    cli.interactive_menu()


if __name__ == "__main__":
    main()
