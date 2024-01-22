import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from usecase.sync_business_timeline import SyncBusinessTimeline as SyncBusinessTimelineUsecase
from util.logging_traceback import logging_traceback
from util.custom_logging import get_logger
from domain.message import BaseMessage
from domain.channel import Channel

SHORTCUT_ID = "sync-times"

logger = get_logger(__name__)

def just_ack(ack: Ack):
    ack()

def sync_times(body: dict, client: WebClient):
    logger.info("sync_times")
    logger.debug(json.dumps(body))

    try:
        usecase = SyncBusinessTimelineUsecase(original_client = client)
        message = BaseMessage.from_dict(body["message"])
        channel = Channel.from_entity(body["channel"])
        usecase.execute(
            text=message.text,
            original_channel=channel.id,
            original_thread_ts=message.ts,
            file_id_list=[], # TODO: 画像のIDを取得する
        )

    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def shortcut_sync_times(app: App):
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[sync_times],
    )
    return app
