from datetime import timedelta

from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.task import Task, TaskRepository
from domain.task.task_repository import NotionTaskRepository
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from util.datetime import jst_now


# 独自の例外
class StartTaskError(Exception):
    @staticmethod
    def unspecified() -> "StartTaskError":
        return StartTaskError("タスクIDおよびタスクタイトルが未指定です")



class StartTaskUseCase:
    def __init__(self,
                 task_repository: TaskRepository | None = None,
                 google_cal_api: GoogleCalendarApi | None = None) -> None:
        self.task_repository = task_repository or NotionTaskRepository()
        self.google_cal_api = google_cal_api or LambdaGoogleCalendarApi()

    def execute(self, task_id: str | None = None, task_title: str | None = None) -> Task:
        if task_id is None and task_title is None:
            raise StartTaskError.unspecified()
        task = self.load_or_create(task_id, task_title)

        # ポモドーロカウンターをインクリメント
        # FIXME: task.increment_pomodoro_count()を呼び出したあとに保存すればよい
        task = self.task_repository.update_pomodoro_count(task)

        # Googleカレンダーにイベントを登録する
        self._record_google_calendar_achivement(task)

    def load_or_create(self, task_id: str|None = None, task_title: str|None = None) -> Task:
        if task_id is not None:
            return self.task_repository.find_by_id(task_id)
        task = Task.from_title(task_title)
        self.task_repository.save(task)
        return task

    def _record_google_calendar_achivement(self, task: Task) -> None:
        start = jst_now()
        end = start + timedelta(minutes=25)
        front_formatter = f"""---
notion_url: {task.url}
---"""
        self.google_cal_api.post_gas_calendar(
            start=start,
            end=end,
            category="実績",
            title=task.title,
            detail=f"{front_formatter}",
        )
