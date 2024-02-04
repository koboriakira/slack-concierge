import logging
import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from util.logging_traceback import logging_traceback
from util.environment import Environment
from interface.handle_message import handle_message_file_share, handle_message_changed, handle_message_post, handle_message_reply

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

        # ファイル共有イベント
        if event.get("subtype") == "file_share":
            return handle_message_file_share(event, logger, client)

        # メッセージ削除イベントは無視
        if event.get("subtype") == "message_deleted":
            return

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


    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        logging_traceback(e, exc_info)


def handle_message_event(app: App):
    app.event("message")(
        ack=just_ack,
        lazy=[handle],
    )

    return app
