import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from util.logging_traceback import logging_traceback
from util.custom_logging import get_logger
from usecase.start_pomodoro import StartPomodoro as StartPomodoroUsecase
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest

ACTION_ID = "start-pomodoro"

logger = get_logger(__name__)

def just_ack(ack: Ack):
    ack()

def start_pomodoro(body: dict, client: WebClient):
    logger.info("start_pomodoro")
    try:
        action = body["actions"][0]
        notion_page_block_id = action["value"]

        channel_id = body["channel"]["id"]
        thread_ts = body["message"]["ts"]

        logger.debug(json.dumps(body))
        usecase = StartPomodoroUsecase(notion_api=LambdaNotionApi(), google_api=LambdaGoogleCalendarApi(), client=client)

        event_scheduler_request = PomodoroTimerRequest(
            page_id=notion_page_block_id,
            channel=channel_id,
            thread_ts=thread_ts,
        )
        usecase.handle(request=event_scheduler_request)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def action_start_pomodoro(app: App):
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[start_pomodoro],
    )
    return app
