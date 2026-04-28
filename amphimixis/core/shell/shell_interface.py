"""Shell handler interface."""

from abc import ABC, abstractmethod


class IShellHandler(ABC):
    """Abstract base class for shell handlers."""

    @abstractmethod
    def run(self, command: str) -> None:
        """Run a command in the shell.

        :var str command: Command to be executed.
        """
        raise NotImplementedError

    @abstractmethod
    def stdout_readline(self) -> str:
        """Read a line from the shell stdout.

        :rtype: str
        :return: the next line from stdout
        """
        raise NotImplementedError

    @abstractmethod
    def stderr_readline(self) -> str:
        """Read a line from the shell stderr.

        :rtype: str
        :return: the next line from stderr
        """
        raise NotImplementedError
