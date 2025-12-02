"""Abstract class for printing progress."""

from abc import ABC


class Printer(ABC):
    """Interface for user interface"""

    def step(self, build_id: str):
        """Advance the progress counter by one step"""
        raise NotImplementedError

    def print(self, build_id: str, message: str):
        """Send message to user"""
        raise NotImplementedError


class NullPrinter(Printer):
    """Null implementation of Printer interface"""

    def step(self, build_id: str):
        pass

    def print(self, build_id: str, message: str):
        pass
