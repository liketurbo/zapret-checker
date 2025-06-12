import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(levelname)s | %(asctime)s | %(message)s',
        datefmt='%d/%m/%y %H:%M'
    )

    file_handler = RotatingFileHandler(
        './logs.txt',
        maxBytes=10*1024,  # 10KB
        backupCount=0,
        encoding='utf8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
