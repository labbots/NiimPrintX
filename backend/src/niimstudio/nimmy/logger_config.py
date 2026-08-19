import sys

from loguru import logger

LOG_FORMAT = "<blue>{time}</blue> | <level>{level}</level> | {message}"
VERBOSITY_LEVELS = {0: "INFO", 1: "INFO", 2: "DEBUG", 3: "TRACE"}


def setup_logger(verbose: int = 0) -> None:
    logger.remove()
    level = VERBOSITY_LEVELS.get(verbose, "TRACE")
    logger.add(sys.stderr, colorize=True, format=LOG_FORMAT, level=level)
    if verbose > 0:
        logger.add("nimmy.log", rotation="100 MB", compression="zip", level=level)


def logger_enable(verbose: int) -> None:
    setup_logger(verbose)


def get_logger():
    return logger
