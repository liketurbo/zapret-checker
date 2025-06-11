import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_file_path=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(levelname)s | %(asctime)s | %(message)s',
        datefmt='%d/%m/%y %H:%M'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file_path:
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=100*1024,  # 100KB
            backupCount=1,
            encoding='utf8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
