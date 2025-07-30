#!/usr/bin/env python3
"""
Prompt Template CLI
-------------------

An object-oriented CLI for selecting and rendering YAML-based
prompt templates using Jinja2. Supports:
- Browsing categories and templates interactively.
- Passing variables via command-line arguments.
- Rendering templates with dynamic values.
- Copying the full YAML output to the clipboard.
"""

import os
import yaml
import pyperclip
import argparse
from typing import List, Tuple, Dict
from jinja2 import Template
from rich.console import Console
from InquirerPy import inquirer


class PromptTemplateCLI:
    """
    A CLI tool for browsing and rendering YAML prompt templates.
    """

    def __init__(self, base_dir: str) -> None:
        """
        Initialize the CLI.

        Args:
            base_dir (str): Path to the directory containing template categories.
        """
        self.base_dir = base_dir
        self.console = Console()

    def list_categories(self) -> List[str]:
        """
        List all available template categories.

        Returns:
            List[str]: Folder names representing template categories.
        """
        return [
            d for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
        ]

    def list_templates_with_preview(self, category: str) -> List[Dict[str, str]]:
        """
        List templates in the specified category with name and description preview.

        Args:
            category (str): The category folder name.

        Returns:
            List[Dict[str, str]]: List of dictionaries with formatted template previews.
        """
        folder = os.path.join(self.base_dir, category)
        templates = []
        for f in os.listdir(folder):
            if f.endswith((".yaml", ".yml")):
                file_path = os.path.join(folder, f)
                with open(file_path, "r", encoding="utf-8") as file:
                    data = yaml.safe_load(file)
                    name = data.get("prompt_name", "No name")
                    description = data.get("description", "No description")
                    display = f"{f}\n  name: {name}\n  description: {description}"
                    templates.append({"name": display, "value": f})
        return templates

    def load_template(self, category: str, filename: str) -> Tuple[Dict, str]:
        """
        Load a YAML template and its raw content.

        Args:
            category (str): The template category.
            filename (str): The template filename.

        Returns:
            Tuple[Dict, str]: Parsed YAML as a dictionary and raw content string.
        """
        file_path = os.path.join(self.base_dir, category, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Remove leading '---' if present
        if raw_content.startswith("---"):
            raw_content = raw_content.split("\n", 1)[1]

        return yaml.safe_load(raw_content), raw_content

    @staticmethod
    def render_template(content: str, context: Dict[str, str]) -> str:
        """
        Render a Jinja2 template with the given context.

        Args:
            content (str): Template content as a string.
            context (Dict[str, str]): Variables for substitution.

        Returns:
            str: Rendered template string.
        """
        return Template(content).render(**context)

    @staticmethod
    def parse_args() -> argparse.Namespace:
        """
        Parse CLI arguments.

        Returns:
            argparse.Namespace: Parsed arguments.
        """
        parser = argparse.ArgumentParser(description="Prompt Template CLI")
        parser.add_argument("--category", help="Category (skip menu)")
        parser.add_argument("--template", help="Template filename (skip menu)")
        parser.add_argument(
            "--set", nargs="*", help="Set key=value pairs for template variables"
        )
        return parser.parse_args()

    def interactive_menu(self) -> None:
        """
        Run the interactive CLI menu for selecting and rendering templates.
        """
        args = self.parse_args()
        context: Dict[str, str] = {}

        # Parse key=value pairs into context dictionary
        if args.set:
            for kv in args.set:
                key, value = kv.split("=", 1)
                context[key] = value

        # Select category and template (interactive if not provided)
        if args.category and args.template:
            category = args.category
            template = args.template
        else:
            category = inquirer.select(
                message="Select a category:", choices=self.list_categories()
            ).execute()
            template = inquirer.select(
                message="Select a template:",
                choices=self.list_templates_with_preview(category),
            ).execute()

        # Load and render template
        data, raw_yaml = self.load_template(category, template)
        rendered_prompt = self.render_template(data.get("style_prompt", ""), context)
        rendered_yaml = self.render_template(raw_yaml, context)

        # Display styled preview
        self.console.print("\n[bold yellow]Template Preview:[/bold yellow]")
        self.console.print(f"[bold cyan]name:[/bold cyan] {data.get('prompt_name', '').strip()}")
        self.console.print(f"[bold cyan]description:[/bold cyan] {data.get('description', '').strip()}")
        self.console.print(f"[bold cyan]prompt_content:[/bold cyan] {rendered_prompt.strip()}")

        # Show additional keys dynamically
        for key, value in data.items():
            if key not in ["prompt_name", "description", "style_prompt"]:
                self.console.print(f"[bold cyan]{key}:[/bold cyan] {value}")

        # Show applied variables
        if context:
            applied = ", ".join(f"{k}={v}" for k, v in context.items())
            self.console.print(f"\n[bold magenta]Applied Variables:[/bold magenta] {applied}")

        # Copy full YAML to clipboard
        if inquirer.confirm(message="Copy full YAML to clipboard?", default=True).execute():
            pyperclip.copy(rendered_yaml)
            self.console.print("[bold green]Copied full YAML to clipboard![/bold green]")


def main() -> None:
    """
    Entry point for the CLI.
    """
    cli = PromptTemplateCLI(base_dir=os.path.join(os.path.dirname(__file__), "templates"))
    cli.interactive_menu()


if __name__ == "__main__":
    main()
