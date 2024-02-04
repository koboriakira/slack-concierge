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
    # python -m pomodoro_timer
    logger.debug("debug mode")
    event = {
        "page_id": "89af7291-62d4-4079-a450-78f1d455cd15",
        "channel": "C05F6AASERZ",
        "thread_ts": "1707010671.541529"
    }
    context = {}
    print(handler(event, context))
