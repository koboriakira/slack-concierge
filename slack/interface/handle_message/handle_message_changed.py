from logging import Logger

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.channel.thread import Thread
from domain.user import UserKind
from infrastructure.slack.slack_client_wrapper import SlackClientWrapper
from usecase.analyze_webpage_use_case import AnalyzeWebpageUseCase
from util.environment import Environment


def handle_message_changed(event: dict, logger: Logger, client: WebClient) -> None:
    try:
        channel:str = event["channel"]
        message: dict = event["message"]
        thread_ts = message["ts"]
        if _is_posted_link_in_inbox_channel(channel, message):
            logger.info("inboxチャンネルへのリンク投稿")
            attachment = message["attachments"][0]
            original_url=attachment["original_url"]
            client_wrapper = SlackClientWrapper(client=client, logger=logger)
            if client_wrapper.is_reacted(name="white_check_mark", channel=channel, timestamp=thread_ts):
                logger.info("既にリアクションがついているので処理をスキップします。")
                return
            client_wrapper.reactions_add(name="white_check_mark", channel=channel, timestamp=thread_ts)
            usecase = AnalyzeWebpageUseCase(logger=logger)
            slack_thread = Thread(channel_id=channel, thread_ts=thread_ts)
            usecase.handle(original_url=original_url, attachment=attachment, slack_thread=slack_thread)
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
