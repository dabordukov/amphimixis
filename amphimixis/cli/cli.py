"""CLI"""

from amphimixis import general


# pylint: disable=too-few-public-methods
class CLI(general.IUI):
    """CLI class implementing IUI interface"""

    def print(self, message: str) -> None:
        """Print message to the console

        :param str message: Message to print to the console"""

        print(message)
