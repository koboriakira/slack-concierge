import logging
import os
from datetime import date as Date
from datetime import timedelta

from slack_sdk.web import WebClient

from domain.schedule.schedule import Schedule
from domain.task.task import Task
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.task.notion_task_repository import NotionTaskRepository
from util.datetime import now

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)


google_calendar_api = LambdaGoogleCalendarApi()
notion_api = LambdaNotionApi()


def handler(event, context):
    """
    AWS Lambda での実行に対応するハンドラー関数
    """
    date = now().date() + timedelta(days=1) if event.get("date") is None else Date.fromisoformat(event["date"])

    data = google_calendar_api.get_gas_calendar(date=date)
    if data is None:
        return {"message": "no schedule"}

    schedules = [Schedule.from_entity(d) for d in data]
    for schedule in schedules:
        task = Task.from_schedule(schedule)
        NotionTaskRepository().save(task)
    return {"message": "success"}



if __name__ == "__main__":
    # python -m sync_schedule_to_task
    logger.debug("debug mode")
    event = {
        "date": "2024-02-05",
    }
    print(handler(event, {}))
