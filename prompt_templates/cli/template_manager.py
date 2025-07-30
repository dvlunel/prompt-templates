"""
Template management for the Prompt Template CLI.
Handles loading, listing, and searching YAML templates.
"""

import os
import yaml
from typing import List, Dict, Tuple
from rich.console import Console


class TemplateManager:
    """
    Handles operations related to prompt templates:
    - Listing categories
    - Listing templates (with preview)
    - Searching templates
    - Loading YAML templates
    """

    def __init__(self, base_dir: str, console: Console) -> None:
        self.base_dir = base_dir
        self.console = console

    def list_categories(self) -> List[str]:
        """List all available top-level template categories."""
        return [
            d for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
        ]

    def list_templates_with_preview(
        self,
        category: str = None,
        file_paths: List[str] = None
    ) -> List[Dict[str, str]]:
        """
        List templates with their name and description.
        Can filter by category or accept explicit file paths.
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
                    # Just load YAML — do NOT render placeholders here
                    data = yaml.safe_load(file) or {}
                except yaml.YAMLError:
                    data = {}
                name = data.get("prompt_name", "Unnamed template")
                description = data.get("description", "No description available")
                display = f"{cat}/{filename}\n  name: {name}\n  description: {description}"
                templates.append({"name": display, "value": (cat, filename)})
        return templates

    def load_template(self, category: str, rel_path: str) -> Tuple[Dict, str]:
        """
        Load a YAML template and its raw content.
        Returns both parsed YAML and raw text.
        """
        file_path = os.path.join(self.base_dir, category, rel_path)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        if raw_content.startswith("---"):
            raw_content = raw_content.split("\n", 1)[1]
        return yaml.safe_load(raw_content), raw_content

    def search_templates(self, search_term: str) -> List[str]:
        """
        Search for templates by name, description, or tags.
        Returns a list of matching file paths.
        """
        matches = []
        for root, _, files in os.walk(self.base_dir):
            for f in files:
                if f.endswith((".yaml", ".yml")):
                    full_path = os.path.join(root, f)
                    with open(full_path, "r", encoding="utf-8") as file:
                        try:
                            data = yaml.safe_load(file)
                        except yaml.YAMLError:
                            continue
                        if not isinstance(data, dict):
                            continue
                        desc = data.get("description", "").lower()
                        tags = [t.lower() for t in data.get("tags", [])] if isinstance(data.get("tags"), list) else []
                        filename = f.lower()
                        if (search_term.lower() in desc) or (search_term.lower() in tags) or (search_term.lower() in filename):
                            matches.append(full_path)
        return matches
