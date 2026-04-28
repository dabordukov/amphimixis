"""Module that builds a build based on configuration"""

import os
import pickle

from amphimixis.core import logger
from amphimixis.core.general import IUI, NULL_UI, Build, Project
from amphimixis.core.shell import Shell

_logger = logger.setup_logger("BUILDER")


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    BUILDS_LIST_FILE_NAME = ".builds"

    @staticmethod
    def build(project: Project, ui: IUI = NULL_UI) -> None:
        """The method build all builds"""

        for build in project.builds:
            _logger.info("Build the %s", build.build_name)

            if Builder.build_for_linux(project, build, ui):
                _logger.info("Build passed %s", build.build_name)
            else:
                _logger.info("Build failed %s", build.build_name)

    @staticmethod
    def build_for_linux(project: Project, build: Build, ui: IUI = NULL_UI) -> bool:
        """The method build program on Linux"""

        ui.update_message(build.build_name, "Connecting...")
        shell = Shell(project, build.build_machine, ui=ui).connect()

        # path to build on the machine
        path: str = os.path.join(shell.get_project_workdir(), build.build_name)

        if build.build_machine.address is not None:  # if building on the remote machine
            ui.update_message(
                build.build_name, "Copying project sources to remote machine..."
            )
            if not shell.copy_to_remote(
                os.path.normpath(project.path), "~/amphimixis/"
            ):
                _logger.error("Error in copying source files")
                ui.mark_failed(
                    build_id=build.build_name,
                    error_message="Error in copying source files",
                )
                build.successfully_built = False
                return False

        try:
            ui.update_message(build.build_name, "Building...")
            err, _, stderr = shell.run(f"mkdir -p {path}")

            if len(stderr) >= 1 and len(stderr[0]) != 0:
                _logger.error(
                    "Error in creating directory on current machine: %s",
                    "".join(stderr[0]),
                )

            err, sstdout, sstderr = project.build_system.build(build)
            _logger.info("Building output:\n%s", sstdout)
            _logger.info("Building stderr:\n%s", sstderr)

            if err != 0:
                build.successfully_built = False
                return False
            Builder.remember_build(build)
            return True

        except FileNotFoundError:
            ui.mark_failed(
                build_id=build.build_name, error_message="Build system not found"
            )
            return False

    @staticmethod
    def remember_build(build: Build) -> None:
        """Remember build to Builder.BUILDS_LIST_FILE_NAME "
        "file in working directory

        :param Build build: Build to saving"""
        builds: dict[str, Build] = {}
        try:
            with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as file:
                builds = pickle.load(file)
        except FileNotFoundError:
            pass

        builds[build.build_name] = build
        with open(Builder.BUILDS_LIST_FILE_NAME, "wb") as file:
            pickle.dump(builds, file)

    @staticmethod
    def forget_build(build: Build) -> None:
        """Forget build from Builder.BUILDS_LIST_FILE_NAME "
        "file in working directory

        :param Build build: Build to removing from builds list"""
        builds: dict[str, Build] = {}
        try:
            with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as file:
                builds = pickle.load(file)
        except FileNotFoundError:
            pass

        if build.build_name in builds:
            builds.pop(build.build_name)
        with open(Builder.BUILDS_LIST_FILE_NAME, "wb") as file:
            pickle.dump(builds, file)

    @staticmethod
    def clean(project: Project, build: Build, ui: IUI = NULL_UI) -> bool:
        """Clean build artifacts from build machine

        :param Project project: Project whose build must be cleaned
        :param Build build: Build to clean from build machine
        :rtype: bool
        :return: True if successful cleaned, otherwise False"""
        shell = Shell(project, build.build_machine, ui).connect()
        path: str = os.path.join(shell.get_project_workdir(), build.build_name)
        err, stdout, stderr = shell.run(f"rm -rf {path}")
        if stdout[0]:
            _logger.error("Cleaning stdout: %s", "".join(stdout[0]))
        if err == 0:
            Builder.forget_build(build)
            return True
        if stderr[0]:
            _logger.error("Cleaning stderr: %s", "".join(stderr[0]))
        return False

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))
