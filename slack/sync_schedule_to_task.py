import os
import json
import logging
from datetime import date as Date
from slack_sdk.web import WebClient
from domain.schedule.schedule import Schedule
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
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
    date = now().date()

    data = google_calendar_api.get_gas_calendar(date=date)
    if data is None:
        return {"message": "no schedule"}

    schedules = [Schedule.from_entity(d) for d in data]
    for schedule in schedules:
        create_task(schedule)
    return {"message": "success"}

def create_task(schedule: Schedule) -> None:
    start_time_str = schedule.start.time().strftime("%H:%M")
    title = f"[{start_time_str}] {schedule.title}"
    logger.info(title)
    notion_api.create_task(title=title, start_date=schedule.start, end_date=schedule.end)


if __name__ == "__main__":
    # python -m sync_schedule_to_task
    logger.debug("debug mode")
    event = {
        "date": "2024-02-05"
    }
    print(handler(event, {}))
