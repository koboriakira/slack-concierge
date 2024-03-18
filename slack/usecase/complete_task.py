
from domain.routine.routine_task import RoutineTask
from domain.task.task_repository import TaskRepository
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService


class CompleteTask:
    def __init__(
            self,
            task_repository: TaskRepository) -> None:
        self.task_repository = task_repository
        self.scheduler_client = EventBridgeSchedulerService()

    def handle(self, task_page_id: str) -> None:
        """ タスクを完了する """
        task = self.task_repository.find_by_id(task_id=task_page_id)

        # ステータスを更新
        task.complete()
        self.task_repository.save(task=task)

        # ルーティンタスクであれば、次回のタスクの起票予約を行う
        if task.is_routine:
            # FIXME: タスクのタイトルだけなく、インスタンスごと渡したい
            self._tmp_reserve_next_task(task_title=task.title)

    def _tmp_reserve_next_task(self, task_title: str) -> None:
        """ 次回のタスクの起票予約を行う """
        routine_task = RoutineTask.from_name(name=task_title)
        self.scheduler_client.set_create_task(
            title=task_title,
            datetime=routine_task.datetime_creates_next_task)
