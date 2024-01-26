import boto3
from botocore.exceptions import NoCredentialsError
import logging
import requests
import pathlib
import os

BUCKET_NAME = "koboriakira-bucket"
DIR = "/tmp/slack-concierge"
# /tmp/slack-conciergeがなければ作成する
pathlib.Path(DIR).mkdir(exist_ok=True)

class S3Uploader:
    def __init__(self, logger: logging.Logger) -> None:
        self.s3_client = boto3.client('s3')
        self.logger = logger

    def upload(self, file_name: str, file_url: str) -> None:
        try:
            file_path = f"{DIR}/{file_name}"
            self._download_to_local(file_path, file_url)
            self.s3_client.upload_file(file_path, BUCKET_NAME, file_name)
        except FileNotFoundError as e:
            self.logger.error("ファイルが見つかりませんでした。")
            raise e
        except NoCredentialsError as e:
            self.logger.error("認証情報が不足しています。")
            raise e
        except Exception as e:
            self.logger.error(e)
            raise e

    def _download_to_local(self, file_path: str, file_url: str) -> None:
        """ S3にアップロードするためにローカルにダウンロードする """
        with open(file_path, "wb") as f:
            headers = {
                "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"
            }
            response = requests.get(file_url, headers=headers)
            f.write(response.content)

if __name__ == "__main__":
    # python -m usecase.service.S3Uploader
    usecase = S3Uploader(logger=logging.getLogger(__name__))
    usecase.upload("IMG_1874_squoosh_thumb.jpg", "https://files.slack.com/files-tmb/T04Q3ANUV6V-F06G3H1JDU1-665ea938cb/img_1874_squoosh_800.jpg")
