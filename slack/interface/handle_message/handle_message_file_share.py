from slack_sdk.web import WebClient
from logging import Logger
from usecase.upload_files_to_s3 import UploadFilesToS3
from domain.channel import ChannelType
from domain.user import UserKind
from util.environment import Environment

def handle_message_file_share(event: dict, logger: Logger, client: WebClient):
    if _is_uploaded_file_in_share_channel(event):
        usecase = UploadFilesToS3(client, logger)
        usecase = usecase.execute(
            channel=event["channel"],
            files=event["files"],
            thread_ts=event["ts"]
        )
        return


def _is_uploaded_file_in_share_channel(event: dict) -> bool:
    """
    shareチャンネルへのファイルアップロード
    """
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
