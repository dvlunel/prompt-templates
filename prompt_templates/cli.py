#!/usr/bin/env python3
import os
import yaml
import pyperclip
import argparse
from jinja2 import Template
from rich.console import Console
from InquirerPy import inquirer

console = Console()
BASE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def list_categories():
    return [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]


def list_templates(category):
    folder = os.path.join(BASE_DIR, category)
    return [f for f in os.listdir(folder) if f.endswith((".yaml", ".yml"))]


def load_template(category, filename):
    file_path = os.path.join(BASE_DIR, category, filename)
    with open(file_path, "r") as f:
        raw_content = f.read()
    # Remove leading '---' if present
    if raw_content.startswith("---"):
        raw_content = raw_content.split("\n", 1)[1]
    return yaml.safe_load(raw_content), raw_content


def render_template(content, context):
    """Render Jinja2 placeholders in a template string."""
    template = Template(content)
    return template.render(**context)


def parse_args():
    parser = argparse.ArgumentParser(description="Prompt Template CLI")
    parser.add_argument("--category", help="Category (skip menu)")
    parser.add_argument("--template", help="Template filename (skip menu)")
    parser.add_argument("--set", nargs="*", help="Set key=value pairs for template variables")
    return parser.parse_args()


def interactive_menu():
    args = parse_args()
    context = {}

    # Always parse --set key=value pairs into a dictionary
    if args.set:
        for kv in args.set:
            key, value = kv.split("=", 1)
            context[key] = value

    # If category/template are provided, skip menu, else ask interactively
    if args.category and args.template:
        category = args.category
        template = args.template
    else:
        category = inquirer.select(message="Select a category:", choices=list_categories()).execute()
        template = inquirer.select(message="Select a template:", choices=list_templates(category)).execute()

    data, raw_yaml = load_template(category, template)
    rendered_prompt = render_template(data.get('style_prompt', ''), context)
    rendered_yaml = render_template(raw_yaml, context)

    console.print("\n[bold yellow]Template Preview:[/bold yellow]")

    # Styled keys for main fields
    console.print(f"[bold cyan]name:[/bold cyan] {data.get('prompt_name', '').strip()}")
    console.print(f"[bold cyan]description:[/bold cyan] {data.get('description', '').strip()}")
    console.print(f"[bold cyan]prompt_content:[/bold cyan] {rendered_prompt.strip()}")

    # Print any extra keys dynamically
    for key, value in data.items():
        if key not in ['prompt_name', 'description', 'style_prompt']:
            console.print(f"[bold cyan]{key}:[/bold cyan] {value}")

    # Show applied variables for clarity
    if context:
        applied = ", ".join(f"{k}={v}" for k, v in context.items())
        console.print(f"\n[bold magenta]Applied Variables:[/bold magenta] {applied}")

    # Ask for clipboard copy
    if inquirer.confirm(message="Copy full YAML to clipboard?", default=True).execute():
        pyperclip.copy(rendered_yaml)
        console.print("[bold green]Copied full YAML to clipboard![/bold green]")


def main():
    interactive_menu()
