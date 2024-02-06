import os
import json
import logging
from slack_sdk.web import WebClient
from usecase.complete_task import CompleteTask
from infrastructure.api.lambda_notion_api import LambdaNotionApi

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

complete_task = CompleteTask(
    notion_api=LambdaNotionApi(),
    client=SLACK_BOT,
)

def handler(event, context):
    print("event", event)
    print("records", event["Records"])
    request = json.loads(event["Records"][0]["body"])
    print("request", request)
    page_id = request["page_id"]
    # channel = request["channel"]
    # thread_ts = request["thread_ts"]
    complete_task.handle(block_id=page_id)

if __name__ == "__main__":
    # python -m love_spotify_track
    logger.debug("debug mode")
    event = {}
    context = {}
    print(handler(event, context))
