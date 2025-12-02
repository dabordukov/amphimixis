"""Module that builds a build based on configuration"""

import os

from amphimixis import logger
from amphimixis.general import NullPrinter, Printer
from amphimixis.general.general import Build, Project
from amphimixis.shell.shell import Shell

_logger = logger.setup_logger("BUILDER")


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def build(project: Project) -> None:
        """The method build all builds"""

        for build in project.builds:
            _logger.info("Build the %s", os.path.basename(build.build_path))

            if Builder.build_for_linux(project, build):
                _logger.info("Build passed")
            else:
                _logger.info("Build failed")

    @staticmethod
    def build_for_linux(
        project: Project, build: Build, printer: Printer = NullPrinter()
    ) -> bool:
        """The method build program on Linux"""
        shell = Shell(build.build_machine, printer, build.build_id).connect()

        path: str  # path to build on the machine
        if build.build_machine.address is not None:  # if building on the remote machine
            path = (
                "~/amphimixis/"
                f"{Builder._normbase(project.path)}_builds/"
                f"{Builder._normbase(build.build_path)}"
            )

            printer.print(build.build_id, "Copying project sources to remote machine")
            if not shell.copy_to_remote(
                os.path.normpath(project.path), "~/amphimixis/"
            ):
                _logger.error("Error in copying source files")
                printer.print(build.build_id, "Error in copying source files")
                return False
        else:
            path = f"{build.build_path}"  # if building on the local machine

        try:
            configuration_prompt = project.build_system.get_build_system_prompt(
                project, build
            )
            _logger.info("Configuration with: %s", configuration_prompt)

            runner_prompt = project.runner.get_runner_prompt(project, build, printer)
            _logger.info("Run building with: %s", runner_prompt)

            printer.print(build.build_id, "Building...")
            err, stdout, stderr = shell.run(
                f"mkdir -p {path}",
                f"cd {path}",
                configuration_prompt,
                runner_prompt,
            )

            if len(stderr) >= 1 and len(stderr[0]) != 0:
                _logger.error(
                    "Error in creating directory on current machine: %s",
                    "".join(stderr[0]),
                )

            if len(stderr) >= 2 and len(stderr[1]) != 0:
                _logger.error(
                    "Error in changing current working directory on current machine: %s",
                    "".join(stderr[1]),
                )

            if len(stdout) >= 3:
                _logger.info("Configuration output:\n%s", "".join(stdout[2]))
                _logger.info("Configuration stderr:\n%s", "".join(stderr[2]))

            if len(stdout) >= 4:
                _logger.info("Building output:\n%s", "".join(stdout[3]))
                _logger.info("Building stderr:\n%s", "".join(stderr[3]))

            printer.print(build.build_id, "Built!")
            return err == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))
