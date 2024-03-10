import logging
import os

from fastapi import FastAPI
from mangum import Mangum
from slack_sdk.web import WebClient

from domain.channel import ChannelType
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.start_pomodoro import PomodoroTimerRequest, StartPomodoro
from usecase.start_task import StartTask
from util.environment import Environment

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
notion_api = LambdaNotionApi()
google_calendar_api = LambdaGoogleCalendarApi()

# ログ
logging.basicConfig(level=logging.INFO)
if Environment.is_dev():
    logging.basicConfig(level=logging.DEBUG)

# アプリ設定
app = FastAPI(
    title="My Notion API",
    version="0.0.1",
)

@app.get("/healthcheck")
def healthcheck() -> dict:
    return {"status": "ok"}

@app.post("/task/new/")
def post_task(task_name: str) -> dict:
    start_task = StartTask(notion_api=notion_api, client=slack_client)
    response = start_task.handle_prepare(task_title=task_name)
    thread_ts = response["thread_ts"]
    page_id = response["page_id"]

    channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST

    start_pomodoro = StartPomodoro(notion_api=notion_api, google_api=google_calendar_api, client=slack_client)
    event_scheduler_request = PomodoroTimerRequest(
        page_id=page_id,
        channel=channel.value,
        thread_ts=thread_ts,
    )
    start_pomodoro.handle(request=event_scheduler_request)
    return {"status": "ok"}

handler = Mangum(app, lifespan="off")
