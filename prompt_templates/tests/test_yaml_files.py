import os
import glob
import pytest
import yaml
from rich.console import Console

console = Console()

TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
yaml_files = glob.glob(os.path.join(TEMPLATE_DIR, "**", "*.y*ml"), recursive=True)

def pretty_name(path):
    # Show relative path from templates folder
    return os.path.relpath(path, TEMPLATE_DIR)

@pytest.mark.parametrize("file_path", yaml_files, ids=pretty_name)
def test_yaml_is_valid(file_path):
    """
    Ensures every YAML file in the templates directory can be safely loaded.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            # Assertions
            assert content is not None, "File is empty or invalid YAML"
            assert isinstance(content, dict), "File should contain a YAML dictionary"
            required_fields = ["prompt_name", "description", "style_prompt"]
            for field in required_fields:
                assert field in content, f"Missing required field: {field}"

        # Pretty success output
        console.print(f"[green]✓[/green] {pretty_name(file_path)}")

    except yaml.YAMLError as e:
        # Pretty error output (no giant traceback)
        error_msg = f"{e.problem} at line {e.problem_mark.line + 1}, col {e.problem_mark.column + 1}" if hasattr(e, 'problem_mark') else str(e)
        console.print(f"[red]✗ {pretty_name(file_path)}[/red] - {error_msg}")
        pytest.fail(f"Invalid YAML in {pretty_name(file_path)} - {error_msg}", pytrace=False)
    except AssertionError as e:
        # Pretty failed assertion output
        console.print(f"[red]✗ {pretty_name(file_path)}[/red] - {e}")
        pytest.fail(f"Validation failed for {pretty_name(file_path)} - {e}", pytrace=False)
