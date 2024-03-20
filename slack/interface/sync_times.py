import json

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from domain.channel import Channel
from domain.message import BaseMessage
from usecase.sync_business_timeline import SyncBusinessTimeline as SyncBusinessTimelineUsecase
from util.custom_logging import get_logger
from util.error_reporter import ErrorReporter

SHORTCUT_ID = "sync-times"

logger = get_logger(__name__)

def just_ack(ack: Ack) -> None:
    ack()

def sync_times(body: dict, client: WebClient) -> None:
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

    except:  # noqa: E722
        ErrorReporter().execute()

def shortcut_sync_times(app: App) -> App:
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[sync_times],
    )
    return app
