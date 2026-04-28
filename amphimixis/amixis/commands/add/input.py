"""Add input command."""

# pylint: disable=duplicate-code

import os
import shutil
from pathlib import Path

import yaml

from amphimixis.amixis.templates import CONFIG_TEMPLATE
from amphimixis.amixis.utils import create_temp_file, launch_editor, prompt_continue
from amphimixis.core.general.constants import DEFAULT_CONFIG_PATH
from amphimixis.core.general.tools import get_unique_path
from amphimixis.core.validator import validate


def run_add_input() -> bool:
    """Create input.yml from template using $EDITOR (nano by default).

    Validates after editing; reopens editor on failure. If input.yml exists,
    generates a unique name (input-1.yml, etc.) to avoid overwriting.

    :return: True if configuration saved successfully, False otherwise
    :rtype: bool
    """
    base_path = DEFAULT_CONFIG_PATH
    editor = os.environ.get("EDITOR", "nano")
    current_content = CONFIG_TEMPLATE

    print(f"Opening editor: {editor}")
    print("Edit the configuration and save to validate.")
    print("The editor will reopen if validation fails.\n")

    temp_path = create_temp_file(current_content)
    try:
        while True:
            if not launch_editor(editor, temp_path):
                return False

            if _validate_config(temp_path):
                config_path = get_unique_path(base_path)
                return _save_config(temp_path, config_path)

            print("\nValidation failed. Please fix the errors above.")
            if not prompt_continue():
                return False
    finally:
        if temp_path.exists():
            os.unlink(temp_path)


def _validate_config(temp_path: Path) -> bool:
    """Validate configuration file with error handling.

    :param Path temp_path: Path to the configuration file
    :return: True if valid, False otherwise
    :rtype: bool
    """
    try:
        return validate(str(temp_path))
    except yaml.YAMLError as e:
        print(f"\nError: Invalid YAML syntax: {e}")
        print("Editor will reopen for corrections...")
        return False


def _save_config(temp_path: Path, config_path: Path) -> bool:
    """Save the configuration file to the target location.

    :param Path temp_path: Path to the temporary file
    :param Path config_path: Path to the target configuration file
    :return: True if saved successfully, False otherwise
    :rtype: bool
    """
    try:
        shutil.move(str(temp_path), str(config_path))
    except OSError as e:
        print(f"Error saving file: {e}")
        return False
    print(f"Configuration file {config_path.name} successfully created!")
    return True
