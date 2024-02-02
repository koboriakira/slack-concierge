import os
import json
import logging
from slack_sdk.web import WebClient
from usecase.create_task import CreateTask
from infrastructure.api.lambda_notion_api import LambdaNotionApi

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

def handler(event, context):
    print(event)
    create_task = CreateTask(notion_api=LambdaNotionApi())
    create_task.handle(title=event["title"])

if __name__ == "__main__":
    # python -m sync_schedule_to_task
    logger.debug("debug mode")
    event = {}
    context = {}
    print(handler(event, context))
