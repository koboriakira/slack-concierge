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
ROLE_ARN = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/service-role/Amazon_EventBridge_Scheduler_LAMBDA_ce49a1e7be"

class EventBridgeSchedulerService:
    def __init__(self, logger: logging.Logger) -> None:
        self.events_client = boto3.client('scheduler')
        self.logger = logger

    def set_pomodoro_timer(self, page_id: str, future_datetime: Optional[Datetime] = None) -> None:
        try:
            input_json = json.dumps({"page_id": "page_id"})
            rule_name = self._get_rule_name(page_id=page_id)
            future_datetime = datetime_now() + timedelta(minutes=2) if future_datetime is None else future_datetime

            # スケジューラの作成
            response = self.events_client.create_schedule(
                Name=rule_name,
                ActionAfterCompletion='DELETE',
                ScheduleExpressionTimezone="Asia/Tokyo",
                ScheduleExpression=future_datetime.strftime("cron(%M %H %d %m ? %Y)"),
                Target={
                    'Arn': POMODORO_TIMER_LAMBDA_ARN,
                    'RoleArn': ROLE_ARN,
                    'Input': input_json
                },
                State='ENABLED',
                FlexibleTimeWindow={"Mode": "OFF"},
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
    # python -m usecase.service.event_bridge_scheduler_service
    service = EventBridgeSchedulerService(logger=logging.getLogger(__name__))
    page_id = "page_id"
    service.set_pomodoro_timer(page_id=page_id)
