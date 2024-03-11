import json
import tempfile
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError

from util.custom_logging import get_logger

logger = get_logger(__name__)


class S3Utils:
    BUCKET_NAME = "koboriakira-bucket"
    DIR = tempfile.mkdtemp(prefix="slack-concierge")

    S3_CLIENT = boto3.client("s3")

    @classmethod
    def save(cls: "S3Utils", data: list|dict, file_name: str) -> bool:
        file_path = f"{S3Utils.DIR}/{file_name}"
        with Path(file_path).open("w") as f:
            json.dump(data, f, indent=4)

        # S3にアップロード
        return cls.upload_to_s3(file_path=file_path, file_name=file_name)

    @classmethod
    def upload_to_s3(cls: "S3Utils", file_path: str, file_name: str) -> bool:
        try:
            # ファイルをアップロード
            cls.S3_CLIENT.upload_file(file_path, cls.BUCKET_NAME, file_name)
        except FileNotFoundError:
            logger.exception("ファイルが見つかりませんでした。")
            return False
        except NoCredentialsError:
            logger.exception("認証情報が不足しています。")
            return False
        except Exception as e:
            logger.exception(e)
            return False
        return True

    @classmethod
    def load(cls: "S3Utils", file_name: str) -> list[dict] | None:
        file_path = f"{S3Utils.DIR}/{file_name}"

        # S3からダウンロード
        is_success = cls.download_from_s3(file_name=file_name, file_path=file_path)
        if not is_success:
            logger.error("S3からのダウンロードに失敗しました。")
            return None

        with Path(file_path).open("r") as f:
            return json.load(f)

    @classmethod
    def download_from_s3(cls: "S3Utils", file_name:str, file_path:str) -> bool:
        try:
            # ファイルをダウンロード
            cls.S3_CLIENT.download_file(cls.BUCKET_NAME, file_name, file_path)
        except FileNotFoundError:
            logger.exception("ファイルが見つかりませんでした。")
            return False
        except NoCredentialsError:
            logger.exception("認証情報が不足しています。")
            return False
        except Exception as e:
            logger.exception(e)
            return False
        return True
