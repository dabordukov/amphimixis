"""Add subcommands."""

from argparse import ArgumentParser, Namespace

from amphimixis.amixis.commands.add.input import run_add_input
from amphimixis.amixis.commands.add.toolchain import run_add_toolchain

HELP_MESSAGE = "Add configuration files or toolchains interactively"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for add command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """
    subparsers = parser.add_subparsers(dest="add_subcommand", title="add options")
    subparsers.required = True

    subparsers.add_parser(
        "input",
        help="interactively create input.yml configuration file",
    )

    subparsers.add_parser(
        "toolchain",
        help="interactively add a toolchain to global config",
    )


def run_add(args: Namespace) -> bool:
    """Execute add subcommand.

    :param Namespace args: parsed command line arguments
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """
    add_subcommand = args.add_subcommand

    if add_subcommand == "input":
        return run_add_input()

    if add_subcommand == "toolchain":
        return run_add_toolchain()

    return False
