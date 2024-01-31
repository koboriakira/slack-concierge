import os
import json
import logging
from slack_sdk.web import WebClient
from usecase.pomodoro_timer import PomodoroTimer

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

def handler(event, context):
    print(event)
    pomodoro_timer = PomodoroTimer(client=SLACK_BOT)
    pomodoro_timer.handle(
        notion_page_block_id=event["page_id"],
        channel=event["channel"],
        thread_ts=event["thread_ts"],
    )

if __name__ == "__main__":
    # python -m sync_schedule_to_task
    logger.debug("debug mode")
    event = {}
    context = {}
    print(handler(event, context))
