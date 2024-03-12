import logging

FORMATTER = logging.Formatter('%(message)s')
PERSISTENT_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def setup_logger(
        name: str,
        log_file: str,
        level=logging.INFO,
        formatter=FORMATTER,
        add_stderr: bool = False,
    ) -> logging.Logger:

    handler = logging.FileHandler(log_file, 'w', encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    logger.setLevel(level)
    logger.addHandler(handler)
    if add_stderr:
        logger.addHandler(logging.StreamHandler())

    return logger


def setup_persistent_logger(
        name: str,
        log_file: str,
        level=logging.INFO,
        formatter=PERSISTENT_FORMATTER
    ) -> logging.Logger:

    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
