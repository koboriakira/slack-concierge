from domain.task.task import Task
from domain.task.task_repository import TaskRepository
from usecase.service.slack_user_client import SlackUserClient


class CreateTaskInInbox:
    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository
        self.user_client = SlackUserClient()

    def handle(self, text: str, event_ts: str, channel: str) -> None:
        """ INBOXタスクを作成する """
        title = text if "\n" not in text else text.split("\n")[0]
        task = Task.from_title(title)
        page = self._task_repository.save(task)
        self.user_client.handle(page_id=page.task_id, channel=channel, thread_ts=event_ts)
