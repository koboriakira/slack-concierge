import logging
from logging import Logger
from typing import Optional
import os

LOG_FILE_NAME = "app.log"

def get_logger(name: Optional[str] = None) -> Logger:
    logger = logging.getLogger(name)

    if os.getenv("ENVIRONMENT") == "dev":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # handler1: 標準出力
    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)8s %(message)s"))
    logger.addHandler(handler1)

    # if os.getenv("ENVIRONMENT") == "dev":
    #     # handler2を作成: ファイル出力
    #     handler2 = logging.FileHandler(filename=LOG_FILE_NAME)
    #     handler2.setLevel(logging.DEBUG)
    #     handler2.setFormatter(logging.Formatter(
    #         "%(asctime)s %(levelname)8s %(message)s"))
    #     logger.addHandler(handler2)

    return logger
