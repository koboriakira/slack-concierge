import boto3
from botocore.exceptions import NoCredentialsError
import logging
import requests
import pathlib
import json
import os
from datetime import datetime as Datetime
from datetime import timedelta
from typing import Optional
from util.datetime import now as datetime_now

# BUCKET_NAME = "koboriakira-bucket"
# DIR = "/tmp/slack-concierge"
# /tmp/slack-conciergeがなければ作成する
# pathlib.Path(DIR).mkdir(exist_ok=True)

AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID']
POMODORO_TIMER_LAMBDA_ARN = f"arn:aws:lambda:ap-northeast-1:{AWS_ACCOUNT_ID}:function:SlackConcierge-PomodoroTimer792E3BDD-ZLqpMmL1PeGo"

class EventBridgeService:
    def __init__(self, logger: logging.Logger) -> None:
        self.events_client = boto3.client('events')
        self.logger = logger

    def set_pomodoro_timer(self, page_id: str, future_datetime: Optional[Datetime] = None) -> None:
        try:
            rule_name = self._get_rule_name(page_id=page_id)
            future_datetime = datetime_now() + timedelta(minutes=5) if future_datetime is None else future_datetime
            future_datetime_for_cron = future_datetime - timedelta(hours=9)

            # EventBridgeルールの作成
            response = self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=future_datetime_for_cron.strftime("cron(%M %H %d %m ? %Y)"),
                State='ENABLED',
                Description='Trigger another Lambda function',
            )
            input_json = json.dumps({"page_id": "page_id"})

            # Lambda関数へのターゲットの追加
            self.events_client.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': page_id,
                        'Arn': POMODORO_TIMER_LAMBDA_ARN,
                        'Input': input_json
                    }
                ]
            )
        except NoCredentialsError as e:
            self.logger.error("認証情報が不足しています。")
            raise e
        except Exception as e:
            self.logger.error(e)
            raise e

    def clear_pomodoro_timer(self, page_id: str) -> None:
        rule_name = self._get_rule_name(page_id=page_id)
        try:
            # ルールに関連付けられているターゲットの削除
            response = self.events_client.remove_targets(
                Rule=rule_name,
                Ids=[page_id]
            )

            # ルール自体の削除
            response = self.events_client.delete_rule(
                Name=rule_name
            )
        except NoCredentialsError as e:
            self.logger.error("認証情報が不足しています。")
            raise e
        except Exception as e:
            self.logger.error(e)
            raise e

    def _get_rule_name(self, page_id: str) -> str:
        return f"SlackConcierge-PomodoroTimer-{page_id}"

if __name__ == "__main__":
    # python -m usecase.service.event_bridge_service
    service = EventBridgeService(logger=logging.getLogger(__name__))
    page_id = "page_id"
    # service.set_pomodoro_timer(page_id=page_id)
    service.clear_pomodoro_timer(page_id=page_id)
