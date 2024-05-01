import sys
from loguru import logger

from devtools import debug


def setup_logger():
    logger.remove()
    default_level = "INFO"
    logger.add(sys.stderr, colorize=True, format="<blue>{time}</blue> | <level>{level}</level> | {message}",
               level=default_level)
    logger.add("nimmy.log", rotation="100 MB", compression="zip", level=default_level)


# | Level name | Severity value | Logger method     |
# ---------------------------------------------------
# | TRACE      | 5              | logger.trace()    |
# | DEBUG      | 10             | logger.debug()    |
# | INFO       | 20             | logger.info()     |
# | SUCCESS    | 25             | logger.success()  |
# | WARNING    | 30             | logger.warning()  |
# | ERROR      | 40             | logger.error()    |
# | CRITICAL   | 50             | logger.critical() |
# ---------------------------------------------------
def logger_enable(verbose: int):
    # Mapping verbosity level to Loguru levels
    levels = {0: "INFO", 1: "INFO", 2: "DEBUG", 3: "TRACE"}
    new_level = levels.get(verbose, "DEBUG")

    # Iterate over all handlers and update the level
    for handler_id in list(logger._core.handlers):
        logger.remove(handler_id)

    if verbose != 0:
        # Re-adding handlers with new levels
        logger.add(sys.stdout, colorize=True, format="<blue>{time}</blue> | <level>{level}</level> | {message}",
                   level=new_level)
        logger.add("nimmy.log", rotation="100 MB", compression="zip", level=new_level)


def get_logger():
    return logger
