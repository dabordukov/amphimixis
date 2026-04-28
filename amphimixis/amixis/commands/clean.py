"""Clean command."""

import pickle
from argparse import ArgumentParser, Namespace

from amphimixis.core import Builder
from amphimixis.core.general import Build, Project, tools

HELP_MESSAGE = "Clean build directories"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for clean command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """
    parser.add_argument(
        "build_names",
        nargs="*",
        metavar="BUILD_NAMES",
        help="name of builds to clean (if none, interactive mode)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="clean all builds",
    )


def open_alternate_term() -> None:
    """Switch to the alternate terminal buffer using Xterm control codes."""
    print("\033[?1049h", end="")


def close_alternate_term() -> None:
    """Return to the primary terminal buffer using Xterm control codes."""
    print("\033[?1049l", end="")


def clean(*builds: Build) -> bool:
    """Clean builds directories.

    :param Build builds: variable number of Build objects to clean
    :return: True if all specified builds were cleaned successfully, False otherwise
    :rtype: bool
    """
    project: Project
    try:
        project = tools.get_cache_project()
    except FileNotFoundError:
        print("Project file .project not found")
        return False
    success = True
    for b in builds:
        if not Builder.clean(project, b):
            success = False
    return success


def interactive_clean() -> bool:
    """Enumerate builds names and suggest choose which will be cleaned.

    :return: True if all selected builds were cleaned successfully, False otherwise
    :rtype: bool
    """
    builds: dict[str, Build] = {}
    project: Project
    try:
        project = tools.get_cache_project()
        with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as file:
            builds = pickle.load(file)
    except FileNotFoundError:
        pass

    success = True
    try:
        for i, build_name in enumerate(builds.keys()):
            print(f"{i + 1}.\t{build_name}")
        nums_input = input(
            "Enter the builds numbers to clean (separate by spaces): "
        ).split()
        nums = [int(n) - 1 for n in nums_input]

        for i, build in enumerate(builds.values()):
            if i in nums:
                if Builder.clean(project, build):
                    print(f"{build.build_name} was successfully cleaned")
                else:
                    success = False
                    print(f"{build.build_name} failed to clean")
    except ValueError:
        print("Invalid input. Please enter numbers separated by spaces.")
    except KeyboardInterrupt:
        print("Cancelled")
    return success


def run_clean(args: Namespace) -> bool:
    """Execute clean command.

    :param Namespace args: parsed command line arguments
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """
    builds_dict: dict[str, Build] = {}
    try:
        with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as f:
            builds_dict = pickle.load(f)
    except FileNotFoundError:
        print("No builds remembered.")
        return False

    if args.all:
        return clean(*builds_dict.values())
    if args.build_names:
        to_clean = [b for b in builds_dict.values() if b.build_name in args.build_names]
        if not to_clean:
            print("No matching builds found")
            return False
        return clean(*to_clean)
    return interactive_clean()
