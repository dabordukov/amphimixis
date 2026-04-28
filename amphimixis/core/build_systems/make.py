"""Module working with Make build system."""

import os

from amphimixis.core import logger
from amphimixis.core.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    Toolchain,
)
from amphimixis.core.shell import Shell

_logger = logger.setup_logger("MAKE")


class Make(BuildSystem, IHighLevelBuildSystem, ILowLevelBuildSystem):
    """Implementation of working with Make build system."""

    _GNU_standard_compatibility_warn_msg = (
        "Amphimixis only uses GNU standard flags for Makefile, "
        "if Makefile does not meet this standard, then using your toolchains and"
        " compilation flags may not work, you can fix it manually by specifying "
        "them in the config_flags field in the format used by the current Makefile"
    )

    def _attrs_map(self, tool: str) -> str:
        value = tool.upper().split("_COMPILER", maxsplit=1)[0]
        match value.split("_")[0]:
            case "C":
                if "FLAGS" not in value:
                    value = value.replace("C", "CC", 1)
            case "FORTRAN":
                value = value.replace("FORTRAN", "FC", 1)
            case "ASM":
                value = value.replace("ASM", "AS", 1)
        return "".join(value.split("_"))

    # pylint: disable=duplicate-code
    def _generate_lang_flags(self, flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            ret_flags.append(f"{"".join(self._attrs_map(flag))}='{value}'")
        return " ".join(ret_flags)

    def _generate_toolchain_flags(self, toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            ret_flags.append(f"{self._attrs_map(tool)}='{value}'")
        return " ".join(ret_flags)

    def _get_makefile_name(self, config_flags: str) -> str:
        options = config_flags.split()
        path = "Makefile"
        for i, opt in enumerate(options):
            if i + 1 == len(options):
                break
            if opt == "-f":
                path = options[i + 1]
                break
            if "--file=" in opt or "--makefile=" in opt:
                path = opt[opt.find("=") + 1 :]
                break
        return os.path.basename(path)

    # pylint: disable=too-many-locals
    def _build_install_clean(
        self, build: Build, configure: bool = False
    ) -> tuple[int, str, str]:
        shell = Shell(self._project, build.build_machine, self._ui).connect()
        build_path = os.path.join(shell.get_project_workdir(), build.build_name)
        command = "make "
        cd_dir = build_path
        if configure:
            if build.config_flags is not None:
                command += f"{build.config_flags} "
            if build.compiler_flags is not None:
                command += f"{self._generate_lang_flags(build.compiler_flags)} "
            if build.toolchain is not None:
                if build.toolchain.sysroot is not None:
                    command += f"SYSROOT='{build.toolchain.sysroot}' "
                command += f"{self._generate_toolchain_flags(build.toolchain)} "
            cd_dir = os.path.join(
                shell.get_source_dir(),
                self.find_relative_path(
                    self._get_makefile_name(str(build.config_flags))
                ),
            )
        if build.jobs:
            command += f"--jobs={build.jobs} "

        err, stdout, stderr = shell.run(f"cd {cd_dir}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        _logger.info("Run building with '%s'", command)
        err, stdout, stderr = shell.run(command)
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))
        if configure:
            err_, stdout_, stderr_ = shell.run(
                f"make install DESTDIR={build_path}", "make clean"
            )
            err = err_ if err == 0 else err
            stdout[0].extend([line for cmd_stdout in stdout_ for line in cmd_stdout])
            stderr[0].extend([line for cmd_stderr in stderr_ for line in cmd_stderr])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

    def build(self, build: Build) -> tuple[int, str, str]:
        """Build via Make.

        :param Build build: Build to build
        :rtype: tuple[int, str, str]
        :return: Tuple of error_code, stdout, stderr
        """
        self._ui.send_warning(
            build.build_name,
            Make._GNU_standard_compatibility_warn_msg,
        )
        _logger.warning(Make._GNU_standard_compatibility_warn_msg)

        return self._build_install_clean(build, configure=True)

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run building via Make.

        :param Build build: Build to run building
        :return: Tuple of error code, stdout and stderr
        """
        return self._build_install_clean(build)
