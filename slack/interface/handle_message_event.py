import logging
import re
import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from util.logging_traceback import logging_traceback
from usecase.upload_files_to_s3 import UploadFilesToS3
from usecase.analyze_inbox import AnalyzeInbox
from domain.channel import ChannelType
from domain.user import UserKind
from util.environment import Environment
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.slack.slack_client_wrapper import SlackClientWrapper

def just_ack(ack: Ack):
    ack()

def handle(body: dict, logger: logging.Logger, client: WebClient):
    if Environment.is_dev():
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.DEBUG)
    logger.info("handle_message_event")
    logger.debug(json.dumps(body, ensure_ascii=False))
    client_wrapper = SlackClientWrapper(client=client, logger=logger)

    try:
        event:dict = body["event"]
        if event.get("subtype") == "message_deleted":
            return
        channel:str = event["channel"]
        message: dict = event["message"]
        if is_uploaded_file_in_share_channel(event):
            usecase = UploadFilesToS3(client, logger)
            usecase = usecase.execute(
                channel=channel,
                files=event["files"],
                thread_ts=event["ts"]
            )
        if is_posted_link_in_inbox_channel(channel, message):
            logger.info("inboxチャンネルへのリンク投稿")
            attachment = message["attachments"][0]
            channel = event["channel"]
            thread_ts = event["message"]["ts"]
            if client_wrapper.is_reacted(name="white_check_mark", channel=channel, timestamp=thread_ts):
                logger.info("既にリアクションがついているので処理をスキップします。")
                return
            client_wrapper.reactions_add(channel=channel, name="white_check_mark", timestamp=event["ts"])
            usecase = AnalyzeInbox(client=client, logger=logger, notion_api=LambdaNotionApi())
            usecase.handle(attachment=attachment,
                            channel=channel,
                            thread_ts=thread_ts)
    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        logging_traceback(e, exc_info)


def is_posted_link_in_inbox_channel(channel:str, message: dict) -> bool:
    """
    inboxチャンネルへのリンク投稿
    """
    if channel != ChannelType.INBOX.value:
        return False
    user:str = message["user"]
    if user != UserKind.KOBORI_AKIRA.value:
        return False
    attachments = message.get("attachments")
    if attachments is None or len(attachments) == 0:
        return False
    return True

def is_uploaded_file_in_share_channel(event: dict) -> bool:
    """
    shareチャンネルへのファイルアップロード
    """
    subtype = event.get("subtype")
    if subtype != "file_share":
        return False
    user:str = event["user"]
    if user != UserKind.KOBORI_AKIRA.value:
        return False
    channel = event["channel"]
    if channel != ChannelType.SHARE.value:
        return False
    files = event.get("files")
    if files is None or len(files) == 0:
        return False
    return True



def handle_message_event(app: App):
    app.event("message")(
        ack=just_ack,
        lazy=[handle],
    )

    return app
