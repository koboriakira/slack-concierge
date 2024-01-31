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
    print("Hello")
    page_id = event["page_id"]
    print(page_id)

if __name__ == "__main__":
    # python -m sync_schedule_to_task
    logger.debug("debug mode")
    event = {}
    context = {}
    print(handler(event, context))
