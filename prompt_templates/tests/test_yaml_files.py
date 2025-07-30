import os
import glob
import pytest
import yaml

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
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            content = yaml.safe_load(f)
            assert content is not None, f"{file_path} is empty or invalid YAML"
        except yaml.YAMLError as e:
            pytest.fail(f"YAML parsing failed for {file_path}:\n{e}")
