import os

from slack_sdk.web import WebClient

from domain.task.task_button_service import TaskButtonSerivce
from infrastructure.task.notion_task_repository import NotionTaskRepository
from usecase.list_today_tasks_use_case import ListTasksUseCase
from util.datetime import jst_now
from util.error_reporter import ErrorReporter

slack_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"])
task_button_service = TaskButtonSerivce(
    slack_client=slack_client,
)
use_case = ListTasksUseCase(
    slack_client=slack_client,
    task_repository=NotionTaskRepository(),
    task_button_service=task_button_service)

TODAY = jst_now().date()


def handler(event: dict, context:dict) -> None:  # noqa: ARG001
    try:
        use_case.execute(target_date=TODAY)
    except:  # noqa: E722
        ErrorReporter().execute(message="list_today_tasks_use_case error")
