"""Config initialization (init) command."""

from argparse import ArgumentParser
from pathlib import Path
from shutil import SameFileError, SpecialFileError, copyfile

from amphimixis.amixis.commands.add.input import get_unique_path

HELP_MESSAGE = "Create configuration file by one of samples"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for init command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "sample_name",
        type=str,
        help="name of configuration file sample",
    )


def run_init(sample: str | None) -> bool:
    """Create configuration file by sample.

    :param str sample: Name of configuration file sample
    """

    samples_path = Path(__file__).parent / "../../samples"
    samples = [p.stem for p in samples_path.glob("*")]
    if sample not in samples:
        print(
            f"Sample {sample} does not exist. Available:\n - ",
            "\n - ".join(samples),
            sep="",
        )
        return False
    smpl_name = Path(sample + ".yml")
    smpl_path = samples_path / smpl_name
    adding_config = get_unique_path(Path(".") / smpl_name)
    try:
        copyfile(smpl_path, adding_config)
    except (FileNotFoundError, SameFileError, SpecialFileError, OSError):
        print("Failed to create file")
        return False
    print(f"Created configuration file {adding_config.name}")
    return True
