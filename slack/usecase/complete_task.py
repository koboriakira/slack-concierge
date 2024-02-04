from enum import Enum
from datetime import datetime as Datetime
from datetime import timedelta
from typing import Optional
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain.notion.notion_page import TaskPage
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from util.datetime import now as datetime_now


class RoutineTask(Enum):
    """ ルーティンタスク """
    CLEANING_BATHROOM = "風呂掃除"

    @property
    def datetime_creates_next_task(self) -> Datetime:
        """ 次回のタスクの起票予約日時。00:00は日付のみの指定とする """
        now = datetime_now()
        match self:
            case RoutineTask.CLEANING_BATHROOM:
                target_datetime = now + timedelta(days=7)
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            case _:
                raise NotImplementedError(f"未実装のルーティンタスクです: {self.value}")

    @staticmethod
    def from_name(name: str) -> 'RoutineTask':
        return RoutineTask(name.replace("【ルーティン】", ""))

class CompleteTask:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.client = client
        self.scheduler_client = EventBridgeSchedulerService()

    def handle(self, block_id: str, channel: str, thread_ts: str):
        """ タスクを完了する """
        # ステータスを更新
        self.notion_api.update_status(page_id=block_id, value="Done")

        # ルーティンタスクであれば、次回のタスクの起票予約を行う
        task:TaskPage = self.notion_api.find_task(page_id=block_id)
        if task.is_routine:
            self._reserve_next_task(task_title=task.title)

    def _reserve_next_task(self, task_title: str):
        """ 次回のタスクの起票予約を行う """
        routine_task = RoutineTask.from_name(name=task_title)
        self.scheduler_client.set_create_task(
            task_title=task_title,
            datetime=routine_task.datetime_creates_next_task)

if __name__ == "__main__":
    # python -m usecase.complete_task
    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    import os
    usecase = CompleteTask(notion_api=LambdaNotionApi(), client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]))
    usecase._reserve_next_task(task_title="【ルーティン】風呂掃除")
