import logging
import os
import pathlib
import sys

# このファイルがあるディレクトリをパスに追加
sys.path.append(str(pathlib.Path(__file__).resolve().parent))

# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)
