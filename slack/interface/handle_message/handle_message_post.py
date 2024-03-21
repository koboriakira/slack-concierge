import logging

from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient

from domain.channel import ChannelType
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.create_task_in_inbox import CreateTaskInInbox
from util.slack_client_wrapper import SlackClientWrapperImpl


def handle_message_post(event: dict, logger: logging.Logger, client: WebClient):
    logger.info("スレッド開始")
    channel:str = event["channel"]
    user:str = event["user"]
    event_ts:str = event["ts"]
    text:str = event["text"]
    blocks: list[dict] = event["blocks"]

    if _is_inbox_post(channel=channel, blocks=blocks):
        client_wrapper = SlackClientWrapperImpl(client=client, logger=logger)
        try:
            client_wrapper.reactions_add(name="inbox_tray", channel=channel, timestamp=event_ts, exception_enabled=True)
            usecase = CreateTaskInInbox(notion_api=LambdaNotionApi())
            usecase.handle(text=text, event_ts=event_ts, channel=channel)
            return
        except SlackApiError as e:
            logger.error(f"Slack APIエラー: {e}")
            return


def _is_inbox_post(channel: str, blocks: list[dict]) -> bool:
    """
    INBOXチャンネルへの投稿かどうか判断する
    """
    if channel != ChannelType.INBOX.value:
        return False
    if _is_only_url(blocks):
        return False
    return True


def _is_only_url(blocks: list[dict]) -> bool:
    """
    ブロックがURLのみかどうか判断する
    """
    if len(blocks) != 1:
        return False
    block = blocks[0]
    if block["type"] != "rich_text":
        return False
    elements = block["elements"]
    if len(elements) != 1:
        return False
    element = elements[0]
    if element["type"] != "rich_text_section":
        return False
    elements = element["elements"]
    if len(elements) != 1:
        return False
    element = elements[0]
    if element["type"] != "link":
        return False
    return True
