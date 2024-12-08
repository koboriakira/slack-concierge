import logging

from domain.block import Blocks
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from slack_sdk.web import WebClient
from usecase.append_text_in_notion_page import AppendTextInNotionPage
from usecase.upload_files_to_s3 import UploadFilesToS3


def handle_message_reply(event: dict, logger: logging.Logger, client: WebClient):
    channel: str = event["channel"]
    user: str = event["user"]
    event_ts: str = event["ts"]
    thread_ts: str = event.get("thread_ts") or event_ts
    text: str = event["text"]
    blocks: list[dict] = event["blocks"]
    files = event.get("files") or []

    logger.info("スレッド返信")
    # 親スレッドの投稿を取得
    parent_message_response = client.conversations_replies(
        channel=channel, ts=thread_ts
    )
    parent_message_blocks = Blocks.from_values(
        parent_message_response["messages"][0]["blocks"]
    )
    parent_message_context = parent_message_blocks.get_context()
    if (
        parent_message_context is not None
        and (page_id := parent_message_context.page_id) is not None
    ):
        # 親スレッドがNotionページとひもづいている場合
        upload_files_to_s3 = UploadFilesToS3(client, logger)
        append_text_usecase = AppendTextInNotionPage(
            notion_api=LambdaNotionApi(), upload_files_to_s3=upload_files_to_s3
        )

        append_text_usecase.handle(
            page_id=page_id,
            text=text,
            files=files,
            channel=channel,
            thread_ts=thread_ts,
        )
        return
