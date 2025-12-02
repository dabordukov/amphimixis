"""Module for shell operations."""

import socket
import subprocess
from ctypes import ArgumentError
from typing import List, Self, Tuple

from amphimixis import logger
from amphimixis.general import MachineInfo, NullPrinter, Printer
from amphimixis.shell.local_shell_handler import _LocalShellHandler
from amphimixis.shell.shell_interface import IShellHandler
from amphimixis.shell.ssh_shell_handler import _SSHHandler

_READING_BARRIER_FLAG = "READING_BARRIER_FLAG"


class Shell:
    """Shell class to manage shell operations.

    In case of local machine $SHELL is used as shell.
    """

    def __init__(
        self,
        machine: MachineInfo,
        printer: Printer = NullPrinter(),
        build_id: str = "None",
        connect_timeout=5,
    ):
        self.logger = logger.setup_logger("SHELL")
        self._shell: IShellHandler
        self.machine = machine
        self.printer = printer
        self.build_id = build_id
        self.connect_timeout = connect_timeout

    def connect(self) -> Self:
        """Connect to the shell of the machine."""

        if self.machine.address is None:
            self._shell = _LocalShellHandler()
            return self

        if self.machine.auth is None:
            raise ArgumentError(
                f"Remote machine [{self.machine.address}] has no authentication info"
            )

        try:
            socket.getaddrinfo(self.machine.address, None)
        except socket.gaierror as exception:
            raise ArgumentError(
                f"{self.machine.address} is unknown address"
            ) from exception

        self._shell = _SSHHandler(self.machine, self.connect_timeout)

        return self

    def run(self, *commands: str) -> Tuple[int, List[List[str]], List[List[str]]]:
        """Run the commands through the shell.

        - Execute commands one by one until:
            non-zero return code occurs or
            OR
            all commands have been executed.


        :param str *commands: commands to be executed

        :rtype: Tuple[int, List[List[str]], List[List[str]]]
        :return: A tuple of three :\n
            - :int: error code of the last executed command
            - :List[List[str]]: List[str] is lines of the stdout of an executed command.
            - :List[List[str]]: List[str] is lines of the stderr of an executed command.
        """

        stdout: List[List[str]] = []
        stderr: List[List[str]] = []
        error_code = 0
        for cmd in commands:
            if error_code:
                break
            self._shell.run(cmd)

            # newline added in case of it is missing in the previous output line
            self._shell.run(f'echo "\n{_READING_BARRIER_FLAG}:$?"')
            self._shell.run(f'echo "\n{_READING_BARRIER_FLAG}">&2')
            cmd_stdout: List[str] = []
            cmd_stderr: List[str] = []
            while line := self._shell.stdout_readline():
                self.printer.step(self.build_id)
                if line[: len(_READING_BARRIER_FLAG)] == _READING_BARRIER_FLAG:
                    error_code = int(line[len(_READING_BARRIER_FLAG) + 1 :])
                    del cmd_stdout[-1]
                    break
                cmd_stdout.append(line)
            stdout.append(cmd_stdout)

            while line := self._shell.stderr_readline():
                self.printer.step(self.build_id)
                if line[:-1] == _READING_BARRIER_FLAG:
                    del cmd_stderr[-1]
                    break
                cmd_stderr.append(line)
            stderr.append(cmd_stderr)

        return (error_code, stdout, stderr)

    def copy_to_remote(self, source: str, destination: str) -> bool:
        """Send a file or folder to the target machine
        Absolute paths are needed

        :var str source: absolute path to a file or folder on the host machine
        :var str destination: absolute path to copy a file or folder to on the controlled machine

        :return: True if successfully copied else False
        """
        if self.machine.auth is None:
            _destination = destination
        else:
            _destination = (
                f"{self.machine.auth.username}@{self.machine.address}:{destination}"
            )

        return self._copy(source, _destination)

    def copy_to_host(self, source: str, destination: str) -> bool:
        """Gets a file or folder from the target machine
        Absolute paths are needed

        :var str source: absolute path to a file or folder on the controlled machine
        :var str destination: absolute path to copy a file or folder to on the host machine

        :return: True if successfully copied else False
        """

        if self.machine.auth is None:
            _source = source
        else:
            _source = f"{self.machine.auth.username}@{self.machine.address}:{source}"

        return self._copy(_source, destination)

    def _copy(self, source: str, destination: str) -> bool:
        if self.machine.auth is None:
            port = -1  # should be OK with local copying
            password = "nopasswd"
        else:
            port = self.machine.auth.port
            # if None or empty string, ssh-agent is supposed
            password = self.machine.auth.password or "nopasswd"

        self.logger.info("Copying %s -> %s", source, destination)
        error_code = subprocess.call(
            [
                "sshpass",
                "-p",
                password,
                "rsync",
                "--checksum",
                "--archive",
                "--recursive",
                "--mkpath",
                "--copy-links",
                "--hard-links",
                "--compress",
                "--log-file=./amphimixis.log",
                "--port",
                str(port),
                source,
                destination,
            ]
        )

        if error_code != 0:
            self.logger.error("Error %s -> %s", source, destination)
            return False

        self.logger.info("Success %s -> %s", source, destination)
        return True
