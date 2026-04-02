"""Parser"""

import argparse
import textwrap
from pathlib import Path

YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"
DEFAULT_CONFIG_PATH = Path("input.yml").resolve()


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

        banner = textwrap.dedent(f"""
            {GRAY}*****************************************************************{RESET}

                 {YELLOW}✰  Amphimixis — build automation and profiling tool  ✰{RESET}

            {GRAY}*****************************************************************{RESET}
        """)

        help_text = super().format_help()

        examples = textwrap.dedent("""
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
                
              amixis --compare buildname1.scriptout buildname2.scriptout
                  → Compares two perf output files (.scriptout)
                    and displays the results in the console.

              amixis --compare filename1.scriptout filename2.scriptout --max-rows=10
                  → Compares two perf output files (.scriptout)
                    and displays up to 10 symbols with the biggest delta per event.

              amixis /path/to/folder/with/project --events cycles cache-misses 
                  → Runs the full pipeline and records only the specified perf events.

              amixis /path/to/folder/with/project --profile --events cycles cache-misses 
                  → Runs only the profiling step and records only the specified perf events.

              amixis --compare a.scriptout b.scriptout --events cycles cache-misses
                  → Compares only the specified events from two .scriptout files.
            """)

        return f"{banner}\n{help_text}\n{examples}"


def create_parser():
    """Create parser with parser argiments"""

    parser = argparse.ArgumentParser(
        prog="amixis",
        formatter_class=CustomFormatterClass,
        usage=argparse.SUPPRESS,
        add_help=True,
    )

    parser.add_argument(
        "path",
        nargs="?",
        type=str,
        help="project path (required for analyze/build/profile and main modes)",
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
        const=str(DEFAULT_CONFIG_PATH),
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
        help="profile the performance of builds.",
    )

    parser.add_argument(
        "-c",
        "--compare",
        nargs=2,
        metavar=("FILE1", "FILE2"),
        help="compare two perf output files (.scriptout) and display the results.",
    )

    parser.add_argument(
        "--max-rows",
        type=int,
        default=20,
        help="maximum number of rows(symbols) to display per event in comparison (default: 20).",
    )

    parser.add_argument(
        "--events",
        nargs="*",
        help="space-separated perf events (e.g., cycles cache-misses).\n"
        "With the main pipeline or --profile, records only these events;"
        " with --compare, shows only these events.",
    )

    parser.add_argument(
        "--clean",
        nargs="*",
        metavar="[ build_name_1 [ build_name_2 [ ... ] ] ]",
        help="clean specified builds directories.\n"
        "Clean ALL builds directories with --all.\n"
        "If no builds is specified, then switches to interactive mode.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="used with --clean for cleaning all builds directories.",
    )

    return parser
