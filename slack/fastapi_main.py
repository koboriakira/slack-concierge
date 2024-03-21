import logging
import os

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from slack_sdk.web import WebClient

from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.schedule.achievement_repository_impl import AchievementRepositoryImpl
from usecase.append_context_use_case import AppendContextUseCase
from usecase.start_task_use_case import StartTaskUseCase
from usecase.wake_up_use_case import WakeUpUseCase
from util.environment import Environment
from util.error_reporter import ErrorReporter

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
notion_api = LambdaNotionApi()
google_calendar_api = LambdaGoogleCalendarApi()

# ログ
logging.basicConfig(level=logging.INFO)
if Environment.is_dev():
    logging.basicConfig(level=logging.DEBUG)

# アプリ設定
app = FastAPI(
    title="My Slack API",
    version="0.0.1",
)

@app.get("/healthcheck")
def healthcheck() -> dict:
    return {"status": "ok"}

@app.post("/task/new/")
def post_new_task(task_name: str) -> dict:
    try:
        start_task_use_case = StartTaskUseCase()
        response = start_task_use_case.execute(task_id=None, task_title=task_name)
        return {"id": response.task_id, "title": response.title}
    except:  # noqa: E722
        ErrorReporter.execute()
        return {"status": "error"}

@app.post("/task/start/{task_id}")
def post_start_task(task_id: str) -> dict:
    try:
        start_task_use_case = StartTaskUseCase()
        response = start_task_use_case.execute(task_id=task_id, task_title=None)
        return {"id": response.task_id, "title": response.title}
    except:  # noqa: E722
        ErrorReporter.execute()
        return {"status": "error"}

class PageAddContextRequest(BaseModel):
    data: dict


@app.post("/message/{channel}/{event_ts}/block/add_context")
def post_add_context(
    channel: str,
    event_ts: str,
    request: PageAddContextRequest) -> dict:
    try:
        usecase = AppendContextUseCase()
        usecase.execute(channel=channel, event_ts=event_ts, data=request.data)
        return {"status": "ok"}
    except:  # noqa: E722
        ErrorReporter.execute()
        return {"status": "error"}

@app.post("/wakeup")
def post_wakeup() -> dict:
    try:
        achivement_repository = AchievementRepositoryImpl(google_cal_api=google_calendar_api)
        usecase = WakeUpUseCase(achievement_repository=achivement_repository)
        usecase.execute()
        return {"status": "ok"}
    except:  # noqa: E722
        ErrorReporter.execute()
        return {"status": "error"}

handler = Mangum(app, lifespan="off")
