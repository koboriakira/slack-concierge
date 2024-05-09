from datetime import datetime, timedelta
from logging import getLogger

from slack_sdk.web import WebClient

from domain.task.task import Task
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.task.notion_task_repository import NotionTaskRepository
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from usecase.start_task_use_case import StartTaskUseCase
from util.datetime import now as _now
from util.environment import Environment
from util.error_reporter import ErrorReporter

logger = getLogger(__name__)
logger.setLevel("DEBUG")

client = WebClient(token=Environment.get_slack_bot_token())
usecase = StartTaskUseCase(
    task_repository=NotionTaskRepository(),
    google_cal_api=LambdaGoogleCalendarApi(),
    client=client,
    scheduler_service=EventBridgeSchedulerService(slack_client=client),
    logger=logger,
)


def handler(event: dict, context: dict) -> dict:  # noqa: ARG001
    try:
        now_tasks = _find_task()
        if len(now_tasks) == 0:
            return {"message": "no task"}
        for task in now_tasks:
            usecase.execute(task_id=task.task_id)
        return {"message": "success"}
    except:  # noqa: E722
        ErrorReporter().execute()
        return {"message": "error"}


def _find_task() -> list[Task]:
    from infrastructure.task.notion_task_repository import NotionTaskRepository

    task_repository = NotionTaskRepository()
    tasks = task_repository.fetch_current_tasks()
    now = _now()
    # now = datetime(
    #     year=now.year,
    #     month=now.month,
    #     day=now.day,
    #     hour=9,
    #     minute=55,
    #     tzinfo=now.tzinfo,
    # )
    after_5minutes = now + timedelta(minutes=5)
    return [task for task in tasks if is_valid(task, now, after_5minutes)]


def is_valid(task: Task, started_at: datetime, end_at: datetime) -> bool:
    if task.start_date is None:
        return False
    # 時刻がない場合も無視
    if not isinstance(task.start_date, datetime):
        return False
    return started_at.timestamp() <= task.start_date.timestamp() and task.start_date.timestamp() <= end_at.timestamp()


if __name__ == "__main__":
    print(handler({}, {}))
