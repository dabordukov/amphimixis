"""CLI commands package."""

from amphimixis.amixis.commands import (
    add,
    analyze,
    build,
    clean,
    compare,
    init,
    profile,
    run,
    validate,
)

COMMANDS = {
    "init": init,
    "run": run,
    "analyze": analyze,
    "build": build,
    "profile": profile,
    "validate": validate,
    "compare": compare,
    "clean": clean,
    "add": add,
}
