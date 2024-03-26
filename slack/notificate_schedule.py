from datetime import date, datetime, timedelta

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.channel.thread import Thread
from domain.task.task import Task
from domain.task.task_button_service import TaskButtonSerivce
from infrastructure.schedule.achievement_repository_impl import AchievementRepositoryImpl
from infrastructure.task.notion_task_repository import NotionTaskRepository
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from usecase.start_pomodoro import StartPomodoro as StartPomodoroUsecase
from util.datetime import now as _now
from util.environment import Environment
from util.error_reporter import ErrorReporter

client = WebClient(token=Environment.get_slack_bot_token())
usecase = StartPomodoroUsecase(
    task_button_service=TaskButtonSerivce(slack_client=client),
    achievement_repository=AchievementRepositoryImpl(),
    task_repository=NotionTaskRepository(),
    scheduler_service=EventBridgeSchedulerService(slack_client=client),
)

def handler(event:dict, context:dict) -> dict:  # noqa: ARG001
    try:
        now_tasks = _find_task()
        if len(now_tasks) == 0:
            return {"message": "no task"}
        for task in now_tasks:
            post_task(task)
        return {"message": "success"}
    except:  # noqa: E722
        ErrorReporter().execute()
        return {"message": "error"}

def _find_task() -> list[Task]:
    from infrastructure.task.notion_task_repository import NotionTaskRepository
    task_repository = NotionTaskRepository()
    tasks = task_repository.fetch_current_tasks()
    now = _now()
    # now = Datetime(year=now.year, month=now.month, day=now.day, hour=11, minute=0)
    after_5minutes = now + timedelta(minutes=5)
    return [task for task in tasks if is_valid(task, now, after_5minutes)]

def is_valid(task: Task, started_at: datetime, end_at: datetime) -> bool:
    if task.start_date is None:
        return False
    # 時刻がない場合も無視
    if isinstance(task.start_date, date):
        return False
    return started_at.timestamp() <= task.start_date.timestamp() <= end_at.timestamp()

def post_task(task: Task) -> None:
    channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST
    thread = Thread.create(channel_id=channel.value)
    usecase.handle(task_page_id=task.task_id, slack_thread=thread)


if __name__ == "__main__":
    print(handler({}, {}))
