"""Tests of the configuration validator."""

from pathlib import Path

import pytest
import yaml

from amphimixis.core.validator import validate


@pytest.mark.unit
class TestValidate:
    """Validation must report errors, never crash on malformed input."""

    @pytest.mark.parametrize(
        "content",
        [
            "",  # empty file
            "- just\n- a\n- list\n",  # root is not a dict
            "platforms: null\nrecipes: null\nbuilds: null\n",  # empty sections
            "builds:\n- build_machine: 1\n  run_machine: 1\n  recipe_id: 1\n",
            # ^ builds referencing ids while 'platforms'/'recipes' are absent
        ],
    )
    def test_malformed_config_returns_false_without_crash(
        self, tmp_path: Path, content: str
    ) -> None:
        config_file = tmp_path / "input.yml"
        config_file.write_text(content, encoding="utf-8")

        assert validate(str(config_file)) is False

    @pytest.mark.parametrize(
        "content",
        [
            "platforms:\n- 1\n  # a non-dict platform entry\nrecipes:\n- id: 1\n"
            '  config_flags: "-O2"\nbuilds:\n- build_machine: 1\n'
            "  run_machine: 1\n  recipe_id: 1\n",
        ],
    )
    def test_non_dict_entries_return_false_without_crash(
        self, tmp_path: Path, content: str
    ) -> None:
        config_file = tmp_path / "input.yml"
        config_file.write_text(content, encoding="utf-8")

        assert validate(str(config_file)) is False

    def test_minimal_valid_config_returns_true(self, tmp_path: Path) -> None:
        config = {
            "platforms": [{"id": 1, "arch": "x86"}],
            "recipes": [{"id": 1, "config_flags": "-DCMAKE_BUILD_TYPE=Release"}],
            "builds": [
                {"build_machine": 1, "run_machine": 1, "recipe_id": 1},
            ],
        }
        config_file = tmp_path / "input.yml"
        config_file.write_text(yaml.safe_dump(config), encoding="utf-8")

        assert validate(str(config_file)) is True

    def test_relative_toolchain_sysroot_is_rejected(self, tmp_path: Path) -> None:
        """A relative sysroot passes validation today but crashes configurator."""
        config = {
            "platforms": [{"id": 1, "arch": "x86"}],
            "recipes": [
                {
                    "id": 1,
                    "config_flags": "-DCMAKE_BUILD_TYPE=Release",
                    "toolchain": {"sysroot": "relative/root"},
                },
            ],
            "builds": [
                {"build_machine": 1, "run_machine": 1, "recipe_id": 1},
            ],
        }
        config_file = tmp_path / "input.yml"
        config_file.write_text(yaml.safe_dump(config), encoding="utf-8")

        assert validate(str(config_file)) is False

    def test_absolute_toolchain_sysroot_is_accepted(self, tmp_path: Path) -> None:
        config = {
            "platforms": [{"id": 1, "arch": "x86"}],
            "recipes": [
                {
                    "id": 1,
                    "config_flags": "-DCMAKE_BUILD_TYPE=Release",
                    "toolchain": {
                        "sysroot": "/opt/sysroot",
                        "cxx_compiler": "/usr/bin/g++",
                    },
                },
            ],
            "builds": [
                {"build_machine": 1, "run_machine": 1, "recipe_id": 1},
            ],
        }
        config_file = tmp_path / "input.yml"
        config_file.write_text(yaml.safe_dump(config), encoding="utf-8")

        assert validate(str(config_file)) is True
