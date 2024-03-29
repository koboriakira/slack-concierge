import logging
from slack_sdk.web import WebClient
from usecase.service.S3Uploader import S3Uploader

CLOUDFRONT_URL = "https://d3swar8tu7yuby.cloudfront.net"

class UploadFilesToS3:
    def __init__(self, client: WebClient, logger: logging.Logger):
        self.client = client
        self.logger = logger
        self.s3_uploader = S3Uploader(logger=logger)

    def execute(self, channel: str, files: list[dict], thread_ts: str = None) -> list[str]:
        """
        Slackに投稿された画像ファイルをS3にアップロードする
        """
        self.logger.info("upload_files_to_s3")

        self._reaction(name="eyes", channel=channel, thread_ts=thread_ts)

        for file in files:
            # 画像以外はスキップ
            # NOTE: 将来的には動画もアップロードしたい
            mine_type: str = file["mimetype"]
            if not mine_type.startswith("image/"):
                continue

            cloudfront_url_list :list[str] = []

            name = file["name"]
            file_url = file["url_private"]

            # 先にサムネイルもあればアップロードする
            thumb_file_url = file["thumb_800"] if "thumb_800" in file else None
            if thumb_file_url is not None:
                thumb_name = convert_thumb_filename(name)
                self.s3_uploader.upload(file_name=thumb_name, file_url=thumb_file_url)
                cloudfront_url_list.append(f"{CLOUDFRONT_URL}/{thumb_name}")

            self.s3_uploader.upload(file_name=name, file_url=file_url)
            cloudfront_url_list.append(f"{CLOUDFRONT_URL}/{name}")

            self._reply(channel=channel, thread_ts=thread_ts, cloudfront_url_list=cloudfront_url_list)

        self._reaction(name="white_check_mark", channel=channel, thread_ts=thread_ts)

    def _reaction(self, name: str, channel: str, thread_ts: str) -> None:
        try:
            self.client.reactions_add(
                channel=channel,
                name=name,
                timestamp=thread_ts
            )
        except Exception as e:
            self.logger.warning("リアクションをつけられませんでした。")

    def _reply(self, channel: str, thread_ts: str, cloudfront_url_list: list[str]) -> None:
        first_url = cloudfront_url_list[0]

        # 最初の画像以外は勝手にプレビューされないよう、コードブロックで囲む
        rest_url_list = cloudfront_url_list[1:] if len(cloudfront_url_list) > 1 else []
        rest_url_text = "\n\n```" + "\n".join(rest_url_list) + "```" if len(rest_url_list) > 0 else ""

        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"{first_url}{rest_url_text}",
        )

def convert_thumb_filename(filename: str) -> str:
    """ "hoge.jpg"を"hoge_thumb.jpg"に変換する """
    return f"{filename.split('.')[0]}_thumb.{filename.split('.')[1]}"


if __name__ == "__main__":
    # python -m usecase.upload_files_to_s3
    import os
    logging.basicConfig(level=logging.INFO)
    logger=logging.getLogger(__name__)
    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)8s %(message)s"))
    logger.addHandler(handler1)

    channel = "C06GDM6NXS4"
    files = [
        {
            "name": "IMG_1874_squoosh.jpg",
            "mimetype": "image/jpeg",
            "url_private": "https://files.slack.com/files-pri/T04Q3ANUV6V-F06G3H1JDU1/img_1874_squoosh.jpg",
            "thumb_800": "https://files.slack.com/files-tmb/T04Q3ANUV6V-F06G3H1JDU1-665ea938cb/img_1874_squoosh_800.jpg",
        }
    ]
    usecase = UploadFilesToS3(client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
                              logger=logger)
    usecase.execute(channel, files)
