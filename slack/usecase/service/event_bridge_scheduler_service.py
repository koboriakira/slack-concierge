import boto3
from botocore.exceptions import NoCredentialsError
import logging
import json
import os
import uuid
from datetime import datetime as Datetime
from datetime import timedelta
from typing import Optional
from util.datetime import now as datetime_now
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest

AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID']
ROLE_ARN = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/SlackConcierge-ScheduleExecutionRoleDFA6D9DF-rsvhjcIYlV8r"

POMODORO_TIMER_LAMBDA_ARN = f"arn:aws:lambda:ap-northeast-1:{AWS_ACCOUNT_ID}:function:SlackConcierge-PomodoroTimer792E3BDD-ZLqpMmL1PeGo"
CREATE_TASK_LAMBDA_ARN = f"arn:aws:lambda:ap-northeast-1:{AWS_ACCOUNT_ID}:function:SlackConcierge-CreateTask0C1E0090-em9csrKc0K9T"

POMODORO_MINUTES = 25

class EventBridgeSchedulerService:
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.events_client = boto3.client('scheduler')
        self.logger = logger or logging.getLogger(__name__)

    def set_pomodoro_timer(self, request: PomodoroTimerRequest) -> None:
        future_datetime = datetime_now() + timedelta(minutes=POMODORO_MINUTES)
        self._create_schedule(
            arn=POMODORO_TIMER_LAMBDA_ARN,
            name=f"pomodoro_timer-{future_datetime.strftime('%H%M')}",
            future_datetime=future_datetime,
            data={
                "page_id": request.page_id,
                "channel": request.channel,
                "thread_ts": request.thread_ts,
            }
        )

    def set_create_task(
            self,
            title: str,
            datetime: Datetime) -> None:

        self._create_schedule(
            arn=CREATE_TASK_LAMBDA_ARN,
            name=f"create_task-{uuid.uuid4()}",
            # イベント（タスク起票）は予定日00:00に行う
            future_datetime=datetime.replace(hour=0, minute=0, second=0, microsecond=0),
            data={
                "title": title,
                # 0時の場合は日付のみが指定されたとする
                "datetime": datetime.isoformat() if datetime.hour == 0 else datetime.date().isoformat()
            }
        )

    def _create_schedule(self,
                         arn: str,
                        name: str,
                        future_datetime: Datetime,
                        data: dict) -> None:
        try:
            self.events_client.create_schedule(
                Name=name,
                ActionAfterCompletion='DELETE',
                ScheduleExpressionTimezone="Asia/Tokyo",
                ScheduleExpression=future_datetime.strftime("cron(%M %H %d %m ? %Y)"),
                Target={
                    'Arn': arn,
                    'RoleArn': ROLE_ARN,
                    'Input': json.dumps(data, ensure_ascii=False)
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

if __name__ == "__main__":
    # python -m usecase.service.event_bridge_scheduler_service
    service = EventBridgeSchedulerService(logger=logging.getLogger(__name__))
    # service.set_pomodoro_timer(page_id="738c86f9-dd70-4b44-99ca-32192f1d8eb9",
    #                             channel="C05F6AASERZ",
    #                             thread_ts="1706682095.204639")
    service.set_create_task(title="風呂掃除【ルーティン】", datetime=datetime_now() + timedelta(days=7))
