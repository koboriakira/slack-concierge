import logging
from dataclasses import dataclass
from uuid import uuid4

from infrastructure.api.lambda_notion_api import LambdaNotionApi
from slack_sdk.web import WebClient
from usecase.service.S3Uploader import S3Uploader

CLOUDFRONT_URL = "https://d3swar8tu7yuby.cloudfront.net"


@dataclass
class ImageUrl:
    original_url: str | None = None
    thumbnail_url: str | None = None

    def append_original_url(self, original_url: str) -> None:
        self.original_url = original_url

    def append_thumbnail_url(self, thumbnail_url: str) -> None:
        self.thumbnail_url = thumbnail_url

    def is_empty(self) -> bool:
        return not self.original_url and not self.thumbnail_url


@dataclass
class UploadFIlesToS3Response:
    image_urls: list[ImageUrl]

    def to_notion_post_data(self) -> dict:
        # thumbnail_urlがNoneの場合は含めない
        images = [
            {"file": image.original_url, "thumbnail": image.thumbnail_url}
            for image in self.image_urls
            if image.thumbnail_url
        ]
        return {"images": images}


# FIXME: 「S3にアップする」みたいな具体的すぎるクラスでないほうがよい
class UploadFilesToS3:
    def __init__(self, client: WebClient, logger: logging.Logger):
        self.client = client
        self.logger = logger
        self.s3_uploader = S3Uploader(logger=logger)
        self._notion_api = LambdaNotionApi(logger=logger)

    def execute(
        self,
        channel: str,
        files: list[dict],
        thread_ts: str,
        only_thumbnail: bool | None = None,
    ) -> UploadFIlesToS3Response:
        """
        Slackに投稿された画像ファイルをS3にアップロードする
        """
        self.logger.info("upload_files_to_s3")

        self._reaction(name="eyes", channel=channel, thread_ts=thread_ts)

        image_urls = []
        for file in files:
            # 画像以外はスキップ

            # NOTE: 将来的には動画もアップロードしたい
            mine_type: str = file["mimetype"]
            if not mine_type.startswith("image/"):
                continue

            cloudfront_url_list: list[str] = []

            name: str = str(uuid4()) + "_" + file["name"]
            name = name.replace(" ", "_")
            file_url = file["url_private"]

            image_url = ImageUrl()
            if not only_thumbnail:
                self.s3_uploader.upload(file_name=name, file_url=file_url)
                cloudfront_url_list.append(f"{CLOUDFRONT_URL}/{name}")
                image_url.append_original_url(f"{CLOUDFRONT_URL}/{name}")

            # サムネイルもあればアップロードする
            if thumb_file_url := self._get_thumb_file_url(file):
                thumb_name = convert_thumb_filename(name)
                thumb_name = thumb_name.replace(" ", "_")
                self.s3_uploader.upload(file_name=thumb_name, file_url=thumb_file_url)
                cloudfront_url_list.append(f"{CLOUDFRONT_URL}/{thumb_name}")
                image_url.append_thumbnail_url(f"{CLOUDFRONT_URL}/{thumb_name}")

            if image_url.is_empty():
                raise Exception(
                    "画像のアップロードに失敗しています。only_thumbnail: %s"
                    % only_thumbnail
                )

            image_urls.append(image_url)
            self._reply(
                channel=channel,
                thread_ts=thread_ts,
                cloudfront_url_list=cloudfront_url_list,
            )

        self._reaction(name="white_check_mark", channel=channel, thread_ts=thread_ts)
        response = UploadFIlesToS3Response(image_urls=image_urls)

        # NotionAPI経由で画像URLをアップロード
        self._notion_api.post(path="/image/", data=response.to_notion_post_data())

        return UploadFIlesToS3Response(image_urls=image_urls)

    def _get_thumb_file_url(self, file: dict) -> str | None:
        if "thumb_800" in file:
            return file["thumb_800"]
        return None

    def _reaction(self, name: str, channel: str, thread_ts: str) -> None:
        try:
            self.client.reactions_add(channel=channel, name=name, timestamp=thread_ts)
        except Exception:
            self.logger.warning("リアクションをつけられませんでした。")

    def _reply(
        self, channel: str, thread_ts: str, cloudfront_url_list: list[str]
    ) -> None:
        first_url = cloudfront_url_list[0]

        # 最初の画像以外は勝手にプレビューされないよう、コードブロックで囲む
        rest_url_list = cloudfront_url_list[1:] if len(cloudfront_url_list) > 1 else []
        rest_url_text = (
            "\n\n```" + "\n".join(rest_url_list) + "```"
            if len(rest_url_list) > 0
            else ""
        )

        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"{first_url}{rest_url_text}",
        )


def convert_thumb_filename(filename: str) -> str:
    # 拡張子を抜いたファイル名の末尾に_thumbをつける
    name, ext = filename.rsplit(".", 1)
    return f"{name}_thumb.{ext}"


if __name__ == "__main__":
    # python -m slack.usecase.upload_files_to_s3
    import os

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
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
    usecase = UploadFilesToS3(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]), logger=logger
    )
    usecase.execute(channel, files, "1731741778.914539")
