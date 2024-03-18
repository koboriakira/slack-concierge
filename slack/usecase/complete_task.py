from slack_sdk.web import WebClient

from domain.infrastructure.api.notion_api import NotionApi
from domain.notion.notion_page import TaskPage
from domain.routine.routine_task import RoutineTask
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService


class CompleteTask:
    def __init__(self, notion_api: NotionApi, client: WebClient) -> None:
        self.notion_api = notion_api
        self.client = client
        self.scheduler_client = EventBridgeSchedulerService()

    def handle(self, block_id: str) -> None:
        """ タスクを完了する """
        # ステータスを更新
        self.notion_api.update_status(page_id=block_id, value="Done")

        # ルーティンタスクであれば、次回のタスクの起票予約を行う
        task:TaskPage = self.notion_api.find_task(task_id=block_id)
        if task.is_routine:
            self._reserve_next_task(task_title=task.title)

    def _reserve_next_task(self, task_title: str) -> None:
        """ 次回のタスクの起票予約を行う """
        routine_task = RoutineTask.from_name(name=task_title)
        self.scheduler_client.set_create_task(
            title=task_title,
            datetime=routine_task.datetime_creates_next_task)
