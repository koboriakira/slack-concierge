import tempfile

import requests
from slack_sdk.web import WebClient


class PostImageUseCase:
    def __init__(
            self,
            slack_bot_client: WebClient) -> None:
        self.slack_bot_client = slack_bot_client


    def execute(
            self,
            image_url: str|list[str],
            channel: str,
            thread_ts: str|None =  None) -> None:
        image_url = image_url if isinstance(image_url, list) else [image_url]
        # 画像をローカルにダウンロードしてからアップロードする
        for url in image_url:
            # 画像ファイルを一時保存
            with tempfile.NamedTemporaryFile(delete=True) as f:
                response = requests.get(url, timeout=30)
                f.write(response.content)
                f.seek(0)
                # 画像をアップロード
                response = self.slack_bot_client.files_upload(
                    channels=channel,
                    file=f.name,
                    thread_ts=thread_ts,
                )
                if thread_ts is None:
                    thread_ts = response["ts"]


if __name__ == "__main__":
    # python -m slack.usecase.slack.post_image_use_case
    import os

    from domain.channel.channel_type import ChannelType
    slack_bot_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    usecase = PostImageUseCase(slack_bot_client)
    usecase.execute(
        image_url="https://pbs.twimg.com/media/GJhdoTjbkAAegbl?format=jpg&name=4096x4096",
        channel=ChannelType.TEST.value,
    )
