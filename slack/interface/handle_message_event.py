import logging
import re
import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from util.logging_traceback import logging_traceback
from usecase.upload_files_to_s3 import UploadFilesToS3
from domain.channel import ChannelType


def just_ack(ack: Ack):
    ack()

def handle(body: dict, logger: logging.Logger, client: WebClient):
    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)8s %(message)s"))
    handler1.setLevel(logging.INFO)
    logger.addHandler(handler1)

    logger.info("handle_message_event")

    try:
        logger.debug(json.dumps(body, ensure_ascii=False))
        event:dict = body["event"]
        if is_uploaded_file_in_share_channel(event):

            usecase = UploadFilesToS3(client, logger)
            usecase = usecase.execute(
                channel=event["channel"],
                files=event["files"],
                thread_ts=event["ts"]
            )

    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        logging_traceback(e, exc_info)

def is_uploaded_file_in_share_channel(event: dict) -> bool:
    """
    shareチャンネルへのファイルアップロード
    """
    subtype = event.get("subtype")
    if subtype != "file_share":
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
