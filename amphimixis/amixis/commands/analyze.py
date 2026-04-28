"""Analyze command."""

from argparse import ArgumentParser
from os import path

from amphimixis.amixis.utils import add_config_arg, add_path_arg
from amphimixis.core.analyzer import analyze
from amphimixis.core.general import IUI, NULL_UI, Project

HELP_MESSAGE = "Analyze the project and detect existing CI, tests, build systems, etc."


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for analyze command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """
    add_path_arg(parser)
    add_config_arg(parser)


def run_analyze(project: Project, ui: IUI = NULL_UI) -> bool:
    """Execute project analysis.

    :param Project project: Project instance to analyze
    :param IUI ui: User interface for progress display
    :return: True if analysis succeeded, False otherwise
    :rtype: bool
    """
    project_name = path.basename(path.normpath(project.path))
    ui.update_message(project_name, "Analyzing project...")

    if not analyze(project):
        ui.mark_failed("Analysis failed. See amphimixis.log for details.")
        return False
    ui.mark_success("Analysis completed! See amphimixis.log for details.")
    return True
