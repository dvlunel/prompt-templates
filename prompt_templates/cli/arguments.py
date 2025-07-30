"""
Argument parsing for the Prompt Template CLI.
"""

import argparse


def parse_args():
    """
    Parse command-line arguments for the CLI.
    """
    parser = argparse.ArgumentParser(description="Prompt Template CLI")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch the interactive menu instead of direct mode",
    )
    parser.add_argument(
        "--category",
        help="Template category to load (skips interactive menu if provided).",
    )
    parser.add_argument(
        "--template",
        help="Template filename to load (requires --category).",
    )
    parser.add_argument(
        "--set",
        nargs="*",
        help="Set key=value pairs for template variables.",
    )
    return parser.parse_args()
