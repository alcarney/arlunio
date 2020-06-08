import collections
import logging

from typing import Optional

_LogConfig = collections.namedtuple("LogConfig", "level,fmt")
_LOG_LEVELS = [
    _LogConfig(level=logging.INFO, fmt="%(message)s"),
    _LogConfig(level=logging.DEBUG, fmt="[%(levelname)s]: %(message)s"),
    _LogConfig(level=logging.DEBUG, fmt="[%(levelname)s][%(name)s]: %(message)s"),
]


def add_console_handler(name: str, verbose: Optional[int] = 0) -> None:
    """Add a console handler for the given logger name"""

    verbose = 0 if verbose < 0 else verbose

    try:
        config = _LOG_LEVELS[verbose]
    except IndexError:
        config = _LOG_LEVELS[-1]

    logger = logging.getLogger(name)
    logger.setLevel(config.level)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(config.fmt))

    logger.addHandler(console)
