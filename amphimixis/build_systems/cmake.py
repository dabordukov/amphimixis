"CMake IBuildSystem implementation"

import os
import queue

from amphimixis import logger
from amphimixis.general import Build, IBuildSystem, Printer, Project

_logger = logger.setup_logger("CMAKE")


class CMake(IBuildSystem):
    """CMake implementation of IBuildSystem"""

    @staticmethod
    def find_cmakelists_path(proj_path: str, max_depth: int = 3) -> str:
        """Find first CMakeLists.txt file relatively project root"""
        q_dirs: queue.Queue[tuple[str, int]] = queue.Queue()
        q_dirs.put((proj_path, 0))
        while not q_dirs.empty():
            curr_dir = q_dirs.get()
            if curr_dir[1] >= max_depth:
                continue
            if os.path.exists(os.path.join(curr_dir[0], "CMakeLists.txt")):
                return curr_dir[0]
            for el in os.scandir(curr_dir[0]):
                if el.is_dir():
                    q_dirs.put((el.path, curr_dir[1] + 1))

        raise FileNotFoundError("Can't find CMakeLists.txt")

    @staticmethod
    def get_build_system_prompt(project: Project, build: Build) -> str:
        """Generate build system prompt with all specified flags"""
        if build.build_machine.address is None:
            cmake_lists_path = os.path.normpath(project.path)
        else:
            cmake_lists_path = f"~/amphimixis/{CMake._normbase(project.path)}"
        try:
            cmake_lists_path += CMake.find_cmakelists_path(project.path)[
                len(os.path.normpath(project.path)) :
            ]
        except FileNotFoundError:
            _logger.error("CMakeLists.txt not found")

        command = "cmake " + cmake_lists_path + " "
        command += build.config_flags
        command += " CXXFLAGS='" + build.compiler_flags + "'"
        command += " CFLAGS='" + build.compiler_flags + "'"
        return command

    @staticmethod
    def get_runner_prompt(project: Project, build: Build, printer: Printer) -> str:
        """Generate runner prompt"""

        raise NotImplementedError

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))
