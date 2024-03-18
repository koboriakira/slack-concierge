import os

from slack_sdk.web import WebClient

from domain.channel.thread import Thread
from domain.task.task_button_service import TaskButtonSerivce
from infrastructure.task.notion_task_repository import NotionTaskRepository
from usecase.pomodoro_timer import PomodoroTimer
from util.error_reporter import ErrorReporter

task_button_service = TaskButtonSerivce(slack_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]))
task_repository = NotionTaskRepository()
usecase = PomodoroTimer(task_button_service=task_button_service, task_repository=task_repository)

def handler(event, context) -> None:  # noqa: ANN001, ARG001
    try:
        page_id=event["page_id"]
        channel=event["channel"]
        thread_ts=event["thread_ts"]

        usecase.handle(
            task_page_id=page_id,
            slack_thread=Thread.create(channel_id=channel, thread_ts=thread_ts))
    except:
        message = f"pomodoro timer error. event: {event}"
        ErrorReporter().execute(message=message)
        raise
