from logging import Logger
from slack_sdk.web import WebClient
from domain.task.task import Task
from domain.infrastructure.api.notion_api import NotionApi
from domain.task.task_repository import TaskRepository
from usecase.service.slack_user_client import SlackUserClient

class CreateTaskInInbox:
    def __init__(self, notion_api: NotionApi, task_repository: TaskRepository):
        self._task_repository = task_repository
        self.user_client = SlackUserClient()

    def handle(self, text: str, event_ts: str, channel: str):
        """ INBOXタスクを作成する """
        title = text if "\n" not in text else text.split("\n")[0]
        task = Task.from_title(title)
        page = self.notion_api.create_task(title=text if "\n" not in text else text.split("\n")[0])
        self.user_client.handle(page_id=page["id"], channel=channel, thread_ts=event_ts)
