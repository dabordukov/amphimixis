"""ConsoleSpinner"""

from amphimixis import general

from .progress_tracker import ProgressTracker


class ConsoleSpinner(general.IUI):
    """ConsoleSpinner"""

    tracker: ProgressTracker

    def __init__(self):
        self.tracker = ProgressTracker()

    def step(self, build_id: str) -> None:
        """Advance spinner animation.

        :param str build_id: Build identifier
        """

        self.tracker.next()
        self.tracker.draw()

    def update_message(self, build_id: str, message: str) -> None:
        """Update message and redraw spinner.

        :param str build_id: Build identifier
        :param str message: Message describing current build phase
        """
        self.tracker.update_message_and_build_id(build_id, message)
        self.tracker.draw()

    def mark_success(self, build_id: str) -> None:
        """Mark current build as successful.

        :param str build_id: Build identifier
        """

        self.tracker.mark_success()
        self.tracker.draw()
        self.tracker.finalize()

    def mark_failed(self, build_id: str, error: str = "") -> None:
        """Mark current build as failed.

        :param str build_id: Build identifier
        :param str error: Error message
        """

        if error == "":
            message = "Failed!"
        else:
            message = error

        self.tracker.mark_failed(message)
        self.tracker.draw()
        self.tracker.finalize()
