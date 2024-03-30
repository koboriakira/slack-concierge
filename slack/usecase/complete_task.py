from domain.task.task_repository import TaskRepository
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService


class CompleteTask:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository
        self.scheduler_client = EventBridgeSchedulerService()

    def handle(self, task_page_id: str) -> None:
        """タスクを完了する"""
        task = self.task_repository.find_by_id(task_id=task_page_id)

        # ステータスを更新
        task.complete()
        self.task_repository.save(task=task)

        # TODO: 実績を更新


if __name__ == "__main__":
    from infrastructure.task.notion_task_repository import NotionTaskRepository

    task_repository = NotionTaskRepository()
    complete_task = CompleteTask(task_repository=task_repository)
    complete_task.handle(task_page_id="5b33e46db6dc4b1f9d88dfec33a3f7c4")
