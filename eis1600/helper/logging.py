from logging import FileHandler, Formatter, getLogger, INFO, Logger

FORMATTER = Formatter('%(message)s')


def setup_logger(name: str, log_file: str, level=INFO, formatter=FORMATTER) -> Logger:

    handler = FileHandler(log_file, 'w', encoding='utf-8')
    handler.setFormatter(formatter)

    logger = getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
