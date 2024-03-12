from logging import Logger

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.channel.thread import Thread
from domain.user import UserKind
from usecase.analyze_webpage_use_case import AnalyzeWebpageUseCase
from util.environment import Environment
from util.slack_client_wrapper import SlackClientWrapperImpl


def handle_message_changed(event: dict, logger: Logger, client: WebClient) -> None:
    try:
        channel:str = event["channel"]
        message: dict = event["message"]
        thread_ts = message["ts"]
        if _is_posted_link_in_inbox_channel(channel, message):
            logger.info("inboxチャンネルへのリンク投稿")
            attachment = message["attachments"][0]
            original_url=attachment["original_url"]
            usecase = AnalyzeWebpageUseCase(
                slack_client_wrapper=SlackClientWrapperImpl(client=client, logger=logger),
                logger=logger)
            usecase.handle(
                original_url=original_url,
                attachment=attachment,
                slack_thread=Thread.create(channel_id=channel, thread_ts=thread_ts),
                )
    except Exception:
        import sys
        import traceback
        exc_info = sys.exc_info()
        t, v, tb = exc_info
        formatted_exception = "\n".join(
            traceback.format_exception(t, v, tb))
        text=f"analyze_inbox: error ```{formatted_exception}```"
        client.chat_postMessage(text=text, channel=channel, thread_ts=thread_ts)

def _is_posted_link_in_inbox_channel(channel:str, message: dict) -> bool:
    """
    inboxチャンネルへのリンク投稿
    """
    if channel != ChannelType.INBOX.value and not Environment.is_dev():
        return False
    user:str = message["user"]
    if user != UserKind.KOBORI_AKIRA.value:
        return False
    if len(message["blocks"]) != 1: # リンク投稿はブロックが1つのみ
        return False
    if (attachments := message.get("attachments")) is None or len(attachments) == 0:
        return False
    return True
