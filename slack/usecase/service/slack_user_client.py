import logging
import os
from typing import Optional
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder

class SlackUserClient:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.Logger(__name__)
        self.user_client = WebClient(token=os.environ["SLACK_USER_TOKEN"])

    def handle(self, page_id: str, channel: str, thread_ts: str):
        """ NotionIDを指定した投稿に埋め込む """
        response = self.user_client.conversations_replies(channel=channel, ts=thread_ts)
        text: str = response["messages"][0]["text"]
        blocks: list[dict] = response["messages"][0]["blocks"]

        # 既存のブロックにコンテクストを埋め込む
        block_builder = BlockBuilder()
        block_builder = block_builder.add_context({
            "page_id": page_id,
        })
        blocks.extend(block_builder.build())

        self.user_client.chat_update(channel=channel,
                                    ts=thread_ts,
                                    text=text,
                                    blocks=blocks)
if __name__ == "__main__":
    # python -m usecase.service.slack_user_client
    from domain.channel import ChannelType
    logging.basicConfig(level=logging.INFO)
    client = SlackUserClient()
    client.handle(page_id="d9f7f4682bc64a8e95158cdded3bbc4d", channel=ChannelType.TEST.value, thread_ts="1706517944.138349")
