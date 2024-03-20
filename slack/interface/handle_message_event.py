import json
import logging

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from interface.handle_message import (
    handle_message_changed,
    handle_message_file_share,
    handle_message_post,
    handle_message_reply,
)
from util.error_reporter import ErrorReporter


def just_ack(ack: Ack) -> None:
    ack()

def handle(body: dict, logger: logging.Logger, client: WebClient) -> None: # noqa: C901
    logger.info("handle_message_event")
    logger.debug(json.dumps(body, ensure_ascii=False))

    try:
        event:dict = body["event"]

        # ファイル共有イベント
        if event.get("subtype") == "file_share":
            return handle_message_file_share(event, logger, client)

        # メッセージ削除イベントは無視
        if event.get("subtype") == "message_deleted":
            return None

        # メッセージ更新イベント
        if event.get("subtype") == "message_changed":
            return handle_message_changed(event, logger, client)

        # メッセージ投稿イベントは、メッセージ投稿とスレッド返信に分ける
        event_ts:str = event["ts"]
        thread_ts: str = event.get("thread_ts") or event_ts
        if event_ts == thread_ts:
            handle_message_post(event, logger, client)
        else:
            handle_message_reply(event, logger, client)
    except:  # noqa: E722
        ErrorReporter().execute()


def handle_message_event(app: App) -> App:
    app.event("message")(
        ack=just_ack,
        lazy=[handle],
    )

    return app
