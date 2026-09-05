"""Opencode subcommands."""

from argparse import ArgumentParser, Namespace

from amphimixis.amixis.commands.opencode.install import run_opencode_install
from amphimixis.amixis.commands.opencode.run import run_opencode_run

HELP_MESSAGE = "Run Amphimixis LLM-agent in Opencode"

_INSTALL_SUBCMD = "install"
_RUN_SUBCMD = "run"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for opencode command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """
    subparsers = parser.add_subparsers(
        dest="opencode_subcommand", title="opencode options"
    )
    subparsers.required = True

    install_parser = subparsers.add_parser(
        _INSTALL_SUBCMD,
        help="install Amphimixis LLM-agent with tools into Opencode locally or globally",
    )
    install_parser.add_argument(
        "-g",
        "--global",
        action="store_true",
        dest="globally",
        help="install globally into XDG_CONFIG_HOME/opencode",
    )

    run_parser = subparsers.add_parser(
        _RUN_SUBCMD,
        help="run Amphimixis LLM-agent in Opencode with a specialized prompt",
    )
    run_parser.add_argument(
        "prompt",
        type=str,
        help="prompt to pass to opencode",
    )


def run_opencode(args: Namespace) -> bool:
    """Execute opencode subcommand.

    :param Namespace args: parsed command line arguments
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """
    opencode_subcommand = args.opencode_subcommand
    if opencode_subcommand == _INSTALL_SUBCMD:
        return run_opencode_install(globally=getattr(args, "globally", False))

    if opencode_subcommand == _RUN_SUBCMD:
        return run_opencode_run(prompt=args.prompt)

    return False
