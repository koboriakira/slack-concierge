import logging
import os

from fastapi import FastAPI
from mangum import Mangum
from slack_sdk.web import WebClient

from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.start_task_use_case import StartTaskUseCase
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
def post_new_task(task_name: str) -> dict:
    start_task_use_case = StartTaskUseCase()
    response = start_task_use_case.execute(task_id=None, task_title=task_name)
    return {"id": response.task_id, "title": response.title}

@app.post("/task/start/{task_id}")
def post_start_task(task_id: str) -> dict:
    start_task_use_case = StartTaskUseCase()
    response = start_task_use_case.execute(task_id=task_id, task_title=None)
    return {"id": response.task_id, "title": response.title}

handler = Mangum(app, lifespan="off")
