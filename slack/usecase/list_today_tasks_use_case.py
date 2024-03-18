
from datetime import date

from domain.channel.channel_type import ChannelType
from domain.channel.thread import Thread
from domain.task.task import Task
from domain.task.task_button_service import TaskButtonSerivce
from domain.task.task_repository import TaskRepository
from util.datetime import jst_now

TODAY = jst_now().date()

class ListTasksUseCase:
    def __init__(
            self,
            task_repository: TaskRepository,
            task_button_service: TaskButtonSerivce) -> None:
        self.task_repository = task_repository
        self.task_button_service = task_button_service

    def execute(
            self,
            target_date: date|None=None,
            slack_thread: Thread|None=None) -> list:
        tasks = self._fetch_tasks(target_date)
        slack_thread = slack_thread or Thread.create(channel_id=ChannelType.TEST)

        for task in tasks:
            self.task_button_service.execute(
                task=task,
                slack_thread=slack_thread,
            )


    def _fetch_tasks(self, target_date: date) -> list[Task]:
        if not target_date:
            raise NotImplementedError("target_date is required")
        if target_date == TODAY:
            return self.task_repository.fetch_current_tasks()
        raise ValueError("target_date must be today")

if __name__ == "__main__":
    # python -m slack.usecase.list_today_tasks_use_case
    import os

    from slack_sdk.web import WebClient

    from infrastructure.task.notion_task_repository import NotionTaskRepository

    task_button_service = TaskButtonSerivce(
        slack_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )
    use_case = ListTasksUseCase(
        task_repository=NotionTaskRepository(),
        task_button_service=task_button_service)
    use_case.execute(target_date=TODAY)
