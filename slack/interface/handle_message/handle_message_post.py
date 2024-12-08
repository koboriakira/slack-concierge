import logging

from domain.channel import ChannelType
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.task.notion_task_repository import NotionTaskRepository
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient
from usecase.create_food_drink_use_case import CreateFoodDrinkUseCase
from usecase.create_task_in_inbox import CreateTaskInInbox
from util.slack_client_wrapper import SlackClientWrapperImpl


def handle_message_post(event: dict, logger: logging.Logger, client: WebClient):
    logger.info("スレッド開始")
    channel: str = event["channel"]
    user: str = event["user"]
    event_ts: str = event["ts"]
    text: str = event["text"]
    blocks: list[dict] = event["blocks"]

    if _is_inbox_post(channel=channel, blocks=blocks):
        client_wrapper = SlackClientWrapperImpl(client=client, logger=logger)
        try:
            client_wrapper.reactions_add(
                name="inbox_tray",
                channel=channel,
                timestamp=event_ts,
                exception_enabled=True,
            )
            usecase = CreateTaskInInbox(task_repository=NotionTaskRepository())
            usecase.handle(text=text, event_ts=event_ts, channel=channel)
            return
        except SlackApiError as e:
            logger.error(f"Slack APIエラー: {e}")
            return

    if _is_food_drink_post(channel=channel):
        client_wrapper = SlackClientWrapperImpl(client=client, logger=logger)
        try:
            client_wrapper.reactions_add(
                name="inbox_tray",
                channel=channel,
                timestamp=event_ts,
                exception_enabled=True,
            )
            usecase = CreateFoodDrinkUseCase(noton_api=LambdaNotionApi())
            usecase.handle(text=text, event_ts=event_ts, channel=channel)
            return
        except SlackApiError as e:
            logger.error(f"Slack APIエラー2: {e}")
            return


def _is_food_drink_post(channel: str) -> bool:
    """
    INBOXチャンネルへの投稿かどうか判断する
    """
    return channel == ChannelType.INBOX.value


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
