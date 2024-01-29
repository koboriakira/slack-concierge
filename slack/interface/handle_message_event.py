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

    try:
        event:dict = body["event"]

        # メッセージ削除イベントは無視
        if event.get("subtype") == "message_deleted":
            return

        # メッセージ更新イベント
        if event.get("subtype") == "message_changed":
            return _handle_message_changed(event, logger, client)

        # メッセージ投稿イベント
        channel:str = event["channel"]
        user:str = event["user"]
        event_ts:str = event["ts"]
        thread_ts: str = event.get("thread_ts") or event_ts
        text:str = event["text"]
        blocks: list[dict] = event["blocks"]
        _handle_message(channel=channel, user=user, event_ts=event_ts, thread_ts=thread_ts, text=text, blocks=blocks, logger=logger, client=client)
    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        logging_traceback(e, exc_info)

def _handle_message(channel:str, user:str, event_ts:str, thread_ts: str, text:str, blocks:list[dict], logger: logging.Logger, client: WebClient):
    if _is_only_url(blocks):
        logger.info("URLのみのメッセージのため、message_changedで処理します")
        return

    logger.debug(f"channel: {channel} user: {user} event_ts: {event_ts} thread_ts: {thread_ts} text: {text}")
    logger.debug(f"blocks: {json.dumps(blocks, ensure_ascii=False)}")
    client_wrapper = SlackClientWrapper(client=client, logger=logger)
    if client_wrapper.is_reacted(name="inbox_tray", channel=channel, timestamp=event_ts):
        logger.info("既にリアクションがついているので処理をスキップします。")
        return
    client_wrapper.reactions_add(name="inbox_tray", channel=channel, timestamp=event_ts)

def _handle_message_changed(event: dict, logger: logging.Logger, client: WebClient):
    # shareチャンネルへのファイルアップロードイベントのみ処理
    if is_uploaded_file_in_share_channel(event):
        usecase = UploadFilesToS3(client, logger)
        usecase = usecase.execute(
            channel=event["channel"],
            files=event["files"],
            thread_ts=event["ts"]
        )
        return

    channel:str = event["channel"]
    message: dict = event["message"]
    if is_posted_link_in_inbox_channel(channel, message):
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
        if Environment.is_dev():
            logger.info("開発環境のため、処理をスキップします。")
            return
        usecase.handle(attachment=attachment,
                        channel=channel,
                        thread_ts=thread_ts)

def is_posted_link_in_inbox_channel(channel:str, message: dict) -> bool:
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
    if channel != ChannelType.SHARE.value and not Environment.is_dev():
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
