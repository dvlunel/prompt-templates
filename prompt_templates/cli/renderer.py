"""
Rendering utilities for Jinja2 templates.
"""

from jinja2 import Template
from typing import Dict


class Renderer:
    """
    Handles rendering of Jinja2-based template content.
    """

    @staticmethod
    def render(content: str, context: Dict[str, str]) -> str:
        """Render a Jinja2 template string with the given context."""
        return Template(content).render(**context)
