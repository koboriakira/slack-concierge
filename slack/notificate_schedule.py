import os
import json
import logging
from datetime import datetime as Datetime
from datetime import timedelta
from slack_sdk.web import WebClient
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from domain.notion.notion_page import TaskPage
from util.datetime import now as _now
from usecase.start_task import StartTask
from usecase.start_pomodoro import StartPomodoro
from domain.channel import ChannelType
from util.environment import Environment

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
notion_api=LambdaNotionApi()
google_api=LambdaGoogleCalendarApi()
start_task_usecase = StartTask(notion_api=notion_api,
                                client=client)
start_pomodoro = StartPomodoro(notion_api=notion_api, google_api=google_api, client=client)

def handler(event, context):
    now = _now()
    # now = Datetime(year=now.year, month=now.month, day=now.day, hour=11, minute=0)
    after_5minutes = now + timedelta(minutes=5)
    tasks = notion_api.list_tasks(start_date=now.date())
    for task in tasks:
        if task.start_date is None:
            continue
        if now.timestamp() <= task.start_date.timestamp() <= after_5minutes.timestamp():
            post_task(task)
    return {"message": "success"}

def post_task(task: TaskPage) -> None:
    # タスクの投稿
    response = start_task_usecase.handle_prepare(task_id=task.id, task_title=task.title)

    # ポモドーロの開始
    channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST
    thread_ts = response["thread_ts"]
    start_pomodoro.handle(notion_page_block_id=task.id, channel=channel.value, thread_ts=thread_ts)
    pass


if __name__ == "__main__":
    logger.debug("debug mode")
    print(handler({}, {}))
