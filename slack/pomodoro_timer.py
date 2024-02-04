import os
import json
import logging
from slack_sdk.web import WebClient
from usecase.pomodoro_timer import PomodoroTimer
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

def handler(event, context):
    print(event)
    pomodoro_timer = PomodoroTimer(client=SLACK_BOT)
    request = PomodoroTimerRequest(
        page_id=event["page_id"],
        channel=event["channel"],
        thread_ts=event["thread_ts"],
    )
    pomodoro_timer.handle(request)

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
