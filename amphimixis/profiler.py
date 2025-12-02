"""Module for profiling executables within a project."""

from enum import Enum

from amphimixis import general, logger, shell
from amphimixis.general import Printer


class Stats(Enum):
    """Profiler stats fields"""

    REAL_TIME = 0
    USER_TIME = 1
    KERNEL_TIME = 2
    EXECUTABLE_RUN_SUCCESS = 3
    PERF_STAT = 4


_commands_args: dict[str, dict[str, str]] = {
    "stat": {
        "cmd": "perf stat",
        "opt": "-ddd -x,",
        "cpu_affinity": "taskset -c 0",
    },
    "record": {"cmd": "perf record", "cpu_affinity": "taskset -c 0"},
    "time": {
        "cmd": "/bin/time",
        "format": '-f"%e\\n%U\\n%S"',
        "cpu_affinity": "taskset -c 0",
    },
}


class Profiler:
    """Class for profiling an executable within a project."""

    def __init__(
        self,
        build: general.Build,
        printer: Printer,
        executable: str = "",
    ):
        self.logger = logger.setup_logger("PROFILER")
        self.machine = build.run_machine
        self.build = build
        self.executable = executable
        self.shell = shell.Shell(self.machine, printer, build.build_id).connect()
        self.stats: dict[Stats, str] = {}

    def execution_time(self) -> bool:
        """Measure execution time: real, user, kernel"""

        error, _, stderr = self.shell.run(f"cd {self.build.build_path}")
        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        command = self._command("time", stderr_clear=False)
        self.logger.info(
            "Measure execution time %s\n\tCommand: %s", self.executable, command
        )
        error, stdout, stderr = self.shell.run(command)
        if error != 0:
            error_message = "STDERR: " + "".join(stderr[0])
            error_message += "STDOUT: " + "".join(stdout[0])
            self.logger.error(error_message)
            return False

        self.stats.update(
            {
                Stats.REAL_TIME: stderr[0][-3],
                Stats.USER_TIME: stderr[0][-2],
                Stats.KERNEL_TIME: stderr[0][-1],
            }
        )
        return True

    def test_executable(self) -> bool:
        """Checks if executable runs and returns no errors"""

        error, stdout, stderr = self.shell.run(f"cd {self.build.build_path}")
        if error != 0:
            error_message = "STDERR: " + "".join(line for cmd in stdout for line in cmd)
            error_message += "STDOUT: " + "".join(
                line for cmd in stderr for line in cmd
            )
            self.logger.error(error_message)

        self.stats.update(
            {Stats.EXECUTABLE_RUN_SUCCESS: "true" if error == 0 else "false"}
        )

        return error == 0

    def perf_stat_collect(self, options: str = "") -> bool:
        """Collect performance statistics using 'perf stat'."""

        error, _, stderr = self.shell.run(
            f"cd {self.build.build_path}",
        )

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        command = self._command("stat", options)
        self.logger.info("Collecting perfomance counters with:\n\t%s", command)
        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Executable returned %d code\n%s", error, "".join(stderr[0])
            )
            return False

        self.stats.update({Stats.PERF_STAT: "".join(stderr[0])})

        return True

    def perf_record_collect(self):
        """Collect performance records using 'perf record'."""
        raise NotImplementedError

    def save_stats(self):
        """Save collected statistics to a file."""
        raise NotImplementedError

    def _command(
        self,
        module: str,
        options: str = "",
        stdout_clear: bool = False,
        stderr_clear: bool = True,
    ) -> str:
        if module not in _commands_args:
            return ""

        command: list[str] = []
        command.append(_commands_args[module]["cmd"])
        if options:
            command.append(options)
        for arg in _commands_args[module]:
            if arg != "cmd":
                command.append(_commands_args[module][arg])

        command.append(f"sh -c './{self.executable}")
        if stdout_clear:
            command.append("1>/dev/null")

        if stderr_clear:
            command.append("2>/dev/null")

        command.append("'")

        return " ".join(command)


if __name__ == "__main__":
    raise NotImplementedError
