import json
import os

from slack_sdk.web import WebClient

from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.complete_task import CompleteTask

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

complete_task = CompleteTask(
    notion_api=LambdaNotionApi(),
    client=SLACK_BOT,
)

def handler(event:dict, context:dict) -> dict:  # noqa: ARG001
    request = json.loads(event["Records"][0]["body"])
    page_id = request["page_id"]
    complete_task.handle(block_id=page_id)
    return {"statusCode": 200}
