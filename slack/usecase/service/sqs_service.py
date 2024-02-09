import boto3
from botocore.exceptions import NoCredentialsError
import logging
import json
from typing import Optional


class SqsService:
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.sqs_client = boto3.client('sqs')
        self.logger = logger or logging.getLogger(__name__)

    def send(
            self,
            queue_url: str,
            message: str|dict) -> None:
        try:
            response = self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message if isinstance(message, str) else json.dumps(message),
            )
        except NoCredentialsError as e:
            self.logger.error("認証情報が不足しています。")
            raise e
        except Exception as e:
            self.logger.error(e)
            raise e


if __name__ == "__main__":
    # python -m usecase.service.sqs_service
    service = SqsService(logger=logging.getLogger(__name__))
    service.send(
        queue_url="https://sqs.ap-northeast-1.amazonaws.com/743218050155/SlackConcierge-LoveSpotifyTrackQueue80A7F4D3-W3eMtBDoeTka",
        message={
            "track_id": "2kxvZpUI34KVcVuVkaKi7d",
            "channel_id": "C05HGA2TK26",
            "thread_ts": "1706691140.672939"
        })
