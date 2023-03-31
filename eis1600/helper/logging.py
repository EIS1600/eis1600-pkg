import logging
from logging import Logger

formatter = logging.Formatter('%(message)s')


def setup_logger(name: str, log_file: str, level=logging.INFO) -> Logger:

    handler = logging.FileHandler(log_file, 'w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
