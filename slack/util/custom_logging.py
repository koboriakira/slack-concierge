import logging
import os
from logging import Logger


def get_logger(name: str | None) -> Logger:
    logger = logging.getLogger(name)  # logger名loggerを取得

    if os.getenv("IS_DEBUG") == "true":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)8s %(message)s"))
    logger.addHandler(handler1)

    # handler2を作成: ファイル出力
    # PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(
    #     os.path.dirname(os.path.abspath(__file__))))
    # log_file_path = f'%s/main.log' % PROJECT_ROOT_PATH
    # if not os.path.exists(log_file_path):
    #     pathlib.Path(log_file_path).touch()
    # handler2 = logging.FileHandler(filename=log_file_path)
    # handler2.setLevel(logging.DEBUG)
    # handler2.setFormatter(logging.Formatter(
    #     "%(asctime)s %(levelname)8s %(message)s"))
    # logger.addHandler(handler2)
    return logger
