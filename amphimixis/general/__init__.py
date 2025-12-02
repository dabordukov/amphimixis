"""The common module that is used in most other modules"""

from amphimixis.general.colors import Colors
from amphimixis.general.general import (
    Arch,
    Build,
    IBuildSystem,
    MachineAuthenticationInfo,
    MachineInfo,
    Printer,
    Project,
)
from amphimixis.general.user_interface import NullPrinter

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "Arch",
    "IBuildSystem",
    "MachineAuthenticationInfo",
    "Colors",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "Printer",
    "NullPrinter",
]
