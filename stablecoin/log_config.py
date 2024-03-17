import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    log_file_path = os.path.join(log_dir, log_file_name)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
    file_handler.suffix = "%Y-%m-%d.log"

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setFormatter(logging.Formatter(log_format))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
