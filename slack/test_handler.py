import os
import json
import logging
from slack_sdk.web import WebClient
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

def handler(event, context):
    event_bridge_scheduler_service = EventBridgeSchedulerService(logger=logger)
    event_bridge_scheduler_service.set_pomodoro_timer(
        page_id="738c86f9-dd70-4b44-99ca-32192f1d8eb9",
        channel="C05F6AASERZ",
        thread_ts="1706682095.204639")


if __name__ == "__main__":
    # python -m sync_schedule_to_task
    logger.debug("debug mode")
    event = {}
    context = {}
    print(handler(event, context))
