"""Module working with Ninja build system."""

import os

from amphimixis.core import logger
from amphimixis.core.general.general import Build, BuildSystem, ILowLevelBuildSystem
from amphimixis.core.shell import Shell

_logger = logger.setup_logger("NINJA")


class Ninja(BuildSystem, ILowLevelBuildSystem):
    """Implementation of working with Ninja build system."""

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run ninja in the build directory.

        :param Build build: Build configuration
        :rtype: tuple[int, str, str]
        :return: Tuple of error_code, stdout, stderr
        """
        shell = Shell(self._project, build.build_machine, self._ui).connect()
        build_path = os.path.join(shell.get_project_workdir(), build.build_name)
        command = "ninja "
        if build.jobs:
            command += f"-j {build.jobs} "
        err, stdout, stderr = shell.run(f"cd {build_path}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))
        _logger.info("Run building with '%s'", command)
        err, stdout, stderr = shell.run(command)

        return (err, "".join(stdout[0]), "".join(stderr[0]))
