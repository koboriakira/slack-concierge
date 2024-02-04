from slack_sdk.web import WebClient
from logging import Logger
from domain.channel import ChannelType
from domain.user import UserKind
from util.environment import Environment
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.slack.slack_client_wrapper import SlackClientWrapper
from usecase.analyze_inbox import AnalyzeInbox


def handle_message_changed(event: dict, logger: Logger, client: WebClient):
    channel:str = event["channel"]
    message: dict = event["message"]
    if _is_posted_link_in_inbox_channel(channel, message):
        logger.info("inboxチャンネルへのリンク投稿")
        attachment = message["attachments"][0]
        channel = event["channel"]
        thread_ts = event["message"]["ts"]
        client_wrapper = SlackClientWrapper(client=client, logger=logger)
        if client_wrapper.is_reacted(name="white_check_mark", channel=channel, timestamp=thread_ts):
            logger.info("既にリアクションがついているので処理をスキップします。")
            return
        client_wrapper.reactions_add(name="white_check_mark", channel=channel, timestamp=thread_ts)
        usecase = AnalyzeInbox(client=client, logger=logger, notion_api=LambdaNotionApi())
        # if Environment.is_dev():
        #     logger.info("開発環境のため、処理をスキップします。")
        #     return
        usecase.handle(attachment=attachment,
                        channel=channel,
                        thread_ts=thread_ts)

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
