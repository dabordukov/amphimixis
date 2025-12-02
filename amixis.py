#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

import argparse
import atexit
import os
import sys
import textwrap
import threading
import time
from pathlib import Path
from typing import Callable

from amphimixis import (
    Builder,
    Printer,
    Profiler,
    analyze,
    build_systems_dict,
    general,
    parse_config,
    validate,
)

YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"


class JobsInformer:
    """Class for informing about alive jobs."""

    lock: threading.Lock
    alive_workers: int
    printer: Printer
    delay: float

    def __init__(self, inform_function: Callable[[], None], delay: float = 0.5):
        self.lock = threading.Lock()
        self.alive_workers = 0
        self.inform_function = inform_function
        self.delay = delay

    def increment_workers(self):
        """Increment the count of alive workers."""
        with self.lock:
            self.alive_workers += 1

    def decrement_workers(self):
        """Decrement the count of alive workers."""
        with self.lock:
            self.alive_workers -= 1

    def inform(self):
        """Inform about alive jobs periodically."""
        while self.alive_workers > 0:
            self.inform_function()
            time.sleep(self.delay)

        self.inform_function()


class PrintToStdout(Printer):
    """Stdout Printer"""

    symbols = ["/", "-", "\\", "|", "/", "-", "\\", "|"]
    build_progress_string = "[{build_id}][{symbol}] {message}"
    counter: list[int]
    build_message: list[str]
    build_id_to_index: dict[str, int]
    number_of_builds: int
    project: general.Project

    def __init__(self, project: general.Project, number_of_builds: int):
        self.project = project
        self.number_of_builds = number_of_builds
        self.build_message = ["None"] * number_of_builds
        self.counter = [0] * number_of_builds
        self.build_id_to_index = {}
        for numeric_id, build in enumerate(project.builds):
            self.build_id_to_index[build.build_id] = numeric_id

    def step(self, build_id: str):
        """Advance the progress counter by one step"""

        self.counter[self.build_id_to_index[build_id]] = (
            self.counter[self.build_id_to_index[build_id]] + 1
        ) % len(self.symbols)

    def print(self, build_id: str, message: str):
        """Send message to user"""

        self.build_message[self.build_id_to_index[build_id]] = message

    def print_data(self):
        """Print progress to stdout"""

        os.system("clear")
        for build in self.project.builds:
            index = self.build_id_to_index[build.build_id]
            print(
                self.build_progress_string.format(
                    build_id=build.build_id,
                    symbol=self.symbols[self.counter[index]],
                    message=self.build_message[index],
                )
            )


class CustomFormatterClass(
    argparse.RawTextHelpFormatter,
):
    """Custom formatter class for argparse to enhance help output."""

    def __init__(self, prog):
        super().__init__(prog, max_help_position=35)

    def _format_action(self, action):
        parts = super()._format_action(action)
        return parts + "\n"

    def format_help(self) -> str:
        """Format help message with custom banner and examples."""

        banner = textwrap.dedent(
            f"""
            {GRAY}*****************************************************************{RESET}

                 {YELLOW}✰  Amphimixis — build automation and profiling tool  ✰{RESET}

            {GRAY}*****************************************************************{RESET}
        """
        )

        help_text = super().format_help()

        examples = textwrap.dedent(
            """
            Examples:

              amixis /path/to/folder/with/project
                  → Main mode. Performs full project analysis, generates configuration files,
                    runs the build process, and performs profiling.

              amixis --analyze /path/to/folder/with/project
                  → Performs project analysis. Detects existing CI, tests, benchmarks, etc.

              amixis --build /path/to/folder/with/project
                  → Builds the project, implicitly calling --configure to generate.
                    configuration files.

              amixis --config=config_file /path/to/folder/with/project
                  → Specifies a custom configuration file to be used for the configuration process;
                    runs all steps including analysis, configuration, building, and profiling.
                    If no config file is specified, defaults to 'input.yml', 
                    which must be located in the working directory.

              amixis --validate=file_name
                  → Checks the config file correctness.

            """
        )

        return f"{banner}\n{help_text}\n{examples}"


def main():
    """Main function for the Amphimixis CLI tool."""

    parser = argparse.ArgumentParser(
        prog="amixis",
        formatter_class=CustomFormatterClass,
        usage=argparse.SUPPRESS,
        add_help=True,
    )

    default_config_path = Path("input.yml").resolve()

    parser.add_argument(
        "path",
        type=str,
        help="path to the project folder to process (required in main mode).",
    )

    parser.add_argument(
        "-v",
        "--validate",
        type=str,
        metavar="FILE",
        default=None,
        help="check correctness of the configuration file.",
    )

    parser.add_argument(
        "--config",
        nargs="?",
        const=str(default_config_path),
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)\n"
        "for all steps: analysis, configuration, building, and profiling.",
    )

    parser.add_argument(
        "-a",
        "--analyze",
        action="store_true",
        help="analyze the project and detect existing CI, tests, build systems, etc.",
    )

    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        help="build the project according to the generated configuration files.",
    )

    parser.add_argument(
        "-p",
        "--profile",
        action="store_true",
        help="profile the performance of builds and compare execution traces",
    )

    args = parser.parse_args()

    if args.config is not None:
        config_file = Path(args.config).expanduser().resolve()
    else:
        config_file = default_config_path

    if args.validate:
        validate(args.validate)
        print(f"{args.validate} is correct!!")
        sys.exit(0)

    if not args.path:
        print("Error: please provide path to the project directory.")
        sys.exit(1)

    project = general.Project(
        str(Path(args.path).expanduser().resolve()),
        [],
        build_systems_dict["make"],
        build_systems_dict["cmake"],
    )

    _secondary_buffer()

    try:
        if not any([args.analyze, args.build, args.profile]):
            analyze(project)
            parse_config(project, config_file_path=str(config_file))
            printer = PrintToStdout(project, len(project.builds))
            informer = JobsInformer(printer.print_data, 0.1)
            threads: list[threading.Thread] = []
            for _, build in enumerate(project.builds):
                # Builder.build_for_linux(project, build, printer)
                # profiler_ = Profiler(project.builds[0], printer)
                # profiler_.execution_time()
                threads.append(
                    threading.Thread(
                        target=_run_all, args=[project, build, printer, informer]
                    )
                )
                # run_all(project, build, printer, informer)
            for thread in threads:
                thread.start()

            time.sleep(0.2)

            informer.inform()

        # if args.analyze:
        #     analyze(project=project)

        # if args.build:
        #     parse_config(project, config_file_path=str(config_file))

        #     for build_id, build in enumerate(project.builds):
        #         Builder.build_for_linux(project, build, printer)

        # if args.profile:
        #     for build_id, build in enumerate(project.builds):
        #         profiler_ = Profiler(project.builds[0], build_id, printer)
        #         profiler_.execution_time()
        #         print(profiler_.stats)

        return 0

    except (FileNotFoundError, ValueError, RuntimeError, LookupError, TypeError) as e:
        _primary_buffer()
        print(f"Error: {e}")
        return 1


def _run_all(
    project: general.Project,
    build: general.Build,
    printer: general.Printer,
    informer: JobsInformer,
):
    informer.increment_workers()
    Builder.build_for_linux(project, build, printer)
    profiler_ = Profiler(project.builds[0], printer)
    if not profiler_.test_executable():
        informer.decrement_workers()
        return

    if not profiler_.execution_time():
        informer.decrement_workers()
        return

    if not profiler_.perf_stat_collect():
        informer.decrement_workers()
        return

    informer.decrement_workers()


def _primary_buffer():
    print("\x1b[?1049l")


def _secondary_buffer():
    print("\x1b[?1049h")


# pylint: disable=invalid-name
if __name__ == "__main__":
    atexit.register(_primary_buffer)
    _error = main()
    input("Press enter to exit...")
    sys.exit(_error)
