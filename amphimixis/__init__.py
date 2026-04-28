"""Amphimixis main module.

Contains two modules:
- `core` contains core application modules
- `cli` is console utility module of Amphimixis
   - `amixis` is the CLI entry point

Assets:
- `samples` contains example configuration files

Other API entities forwards from `core` module for more concise imports:
- general
- build_systems_dict
- analyze
- create_flags
- create_machine
- create_toolchain
- parse_config
- Builder
- Profiler
- Shell
- LaboratoryAssistant
- validate
"""

from amphimixis import amixis, core
from amphimixis.core import general
from amphimixis.core.analyzer import analyze
from amphimixis.core.build_systems import build_systems_dict
from amphimixis.core.builder import Builder
from amphimixis.core.configurator import (
    create_flags,
    create_machine,
    create_toolchain,
    parse_config,
)
from amphimixis.core.laboratory_assistant import LaboratoryAssistant
from amphimixis.core.profiler import Profiler
from amphimixis.core.shell import Shell
from amphimixis.core.validator import validate

# pylint: disable=duplicate-code
__all__ = [
    "general",
    "build_systems_dict",
    "analyze",
    "create_flags",
    "create_machine",
    "create_toolchain",
    "parse_config",
    "Builder",
    "Profiler",
    "Shell",
    "LaboratoryAssistant",
    "validate",
    "core",
    "amixis",
]
