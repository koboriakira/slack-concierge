from datetime import datetime, timedelta

from domain.task.task_repository import TaskRepository
from infrastructure.repository.current_tasks_s3_repository import CurrentTasksS3Repository
from util.datetime import jst_now, now


class FetchCurrentTasksUseCase:
    def __init__(
            self,
            task_repository: TaskRepository | None = None,
            current_tasks_s3_repository: CurrentTasksS3Repository | None = None) -> None:
        self.task_repository = task_repository
        self.current_tasks_s3_repository = current_tasks_s3_repository or CurrentTasksS3Repository()

    def execute(self) -> list:
        current_tasks_cache = self.current_tasks_s3_repository.load()
        if is_expired(current_tasks_cache):
            tasks = self.task_repository.fetch_current_tasks()
            task_options = [
                {"text": t.title_within_50_chars(), "value": t.task_id} for t in tasks if t.title != ""
            ]
            expires_at = now() + timedelta(minutes=5)
            current_tasks_cache = {
                "task_options": task_options,
                "expires_at": expires_at.isoformat(),
            }
            self.current_tasks_s3_repository.save(current_tasks_cache)
        return current_tasks_cache["task_options"]

def is_expired(current_tasks_cache: dict) -> bool:
    if current_tasks_cache is None:
        return True
    expires_at = datetime.fromisoformat(current_tasks_cache["expires_at"])
    return expires_at < jst_now()
