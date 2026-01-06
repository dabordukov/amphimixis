"""Single-line spinner for build progress display"""

import sys


class ProgressTracker:
    """Spinner for progress to user"""

    braille: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    build_id: str
    index: int
    message: str
    status: str

    def __init__(self):
        self.build_id = ""
        self.index = 0
        self.message = ""
        self.status = "running"

    def update_message_and_build_id(self, build_id: str, message: str) -> None:
        """Update build_id and message.

        :param str build_id: Build identifier
        :param str message: Message describing current build phase
        """

        self.build_id = build_id
        self.message = message

    def next(self) -> None:
        """Move to next spinner."""

        self.index = (self.index + 1) % len(self.braille)

    def mark_success(self, message: str = "Success!") -> None:
        """Mark as successful and optionally update message.

        :param str message: Message to display for successful build
        """

        self.status = "success"
        self.message = message

    def mark_failed(self, message: str = "Failed!") -> None:
        """Mark as failed and optionally update message.

        :param str message: Message to display for failed build
        """

        self.status = "failed"
        self.message = message

    def clear(self) -> None:
        """Clear the spinner line."""

        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

    def draw(self) -> None:
        """Render current state to stdout."""

        if self.status == "success":
            symbol = "✓"
        elif self.status == "failed":
            symbol = "✗"
        else:
            symbol = self.braille[self.index]

        sys.stdout.write(f"\r[{self.build_id}][{symbol}] {self.message}")
        sys.stdout.flush()

    def finalize(self) -> None:
        """Move to next line."""

        sys.stdout.write("\n")
        sys.stdout.flush()
