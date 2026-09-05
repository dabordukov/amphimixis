"""Tests of the opencode command dispatcher."""

from argparse import Namespace

import pytest

from amphimixis.amixis.commands.opencode import run_opencode


@pytest.mark.unit
class TestOpencodeCommand:
    """Check that subcommands are dispatched to the correct handlers."""

    def test_run_subcommand_dispatches_without_global_flag(self, mocker) -> None:
        """The `run` subcommand namespace has no `globally` attribute."""
        run_mock = mocker.patch(
            "amphimixis.amixis.commands.opencode.run_opencode_run",
            return_value=True,
        )
        install_mock = mocker.patch(
            "amphimixis.amixis.commands.opencode.run_opencode_install"
        )

        args = Namespace(opencode_subcommand="run", prompt="some prompt")

        assert run_opencode(args) is True
        run_mock.assert_called_once_with(prompt="some prompt")
        install_mock.assert_not_called()

    def test_install_subcommand_dispatches_with_global_flag(self, mocker) -> None:
        """The `install` subcommand passes its `--global` flag through."""
        run_mock = mocker.patch("amphimixis.amixis.commands.opencode.run_opencode_run")
        install_mock = mocker.patch(
            "amphimixis.amixis.commands.opencode.run_opencode_install",
            return_value=True,
        )

        args = Namespace(opencode_subcommand="install", globally=True)

        assert run_opencode(args) is True
        install_mock.assert_called_once_with(globally=True)
        run_mock.assert_not_called()
