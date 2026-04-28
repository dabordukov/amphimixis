"""Validate command."""

from argparse import ArgumentParser

from amphimixis.core.general import IUI, NULL_UI
from amphimixis.core.validator import validate

HELP_MESSAGE = "Check correctness of the configuration file"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for validate command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """
    parser.add_argument(
        "config_file",
        type=str,
        metavar="FILE",
        help="path to the configuration file",
    )


def validate_cmd(args, ui: IUI = NULL_UI) -> bool:
    """Check correctness of the configuration file.

    :param Namespace args: parsed command line arguments
    :param IUI ui: User interface for progress display
    :return: True if validation succeeded, False otherwise
    :rtype: bool
    """
    ui.update_message("Config", f"Validate {args.config_file}...")

    if not validate(args.config_file, ui):
        ui.mark_failed(f"{args.config_file} is incorrect! See amphimixis.log")
        return False
    ui.mark_success(f"{args.config_file} is correct!")
    return True
