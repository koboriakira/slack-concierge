import os
import json
import logging
from datetime import datetime as Datetime
from datetime import timedelta
from slack_sdk.web import WebClient
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from domain.notion.notion_page import TaskPage
from util.datetime import now as _now
from usecase.start_task import StartTask

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

notion_api=LambdaNotionApi()
start_task_usecase = StartTask(notion_api=notion_api,
                               client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]))

def handler(event, context):
    now = _now()
    now = Datetime(year=now.year, month=now.month, day=now.day, hour=16, minute=0)
    after_5minutes = now + timedelta(minutes=5)
    tasks = notion_api.list_tasks(start_date=now.date())
    for task in tasks:
        if task.start_date is None:
            continue
        if now.timestamp() <= task.start_date.timestamp() <= after_5minutes.timestamp():
            post_task(task)
    return {"message": "success"}

def post_task(task: TaskPage) -> None:
    start_task_usecase.handle_prepare(task_id=task.id, task_title=task.title)
    pass


if __name__ == "__main__":
    logger.debug("debug mode")
    print(handler({}, {}))
