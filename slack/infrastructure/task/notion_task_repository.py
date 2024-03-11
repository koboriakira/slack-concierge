

from domain.task import Task, TaskRepository
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from util.environment import Environment


class NotionTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self.api = LambdaNotionApi()

    def find_by_id(self, task_id: str) -> "Task":
        response = self.api.get(path=f"task/{task_id}")
        return Task.reconstruct(data=response["data"])

    def save(self, task: "Task") -> "Task":
        response = self.api.post(path="task",
                                  data=task.to_dict()) if not Environment.is_demo() else _demo_save(task)
        if task.task_id:
            return task

        # タスクIDがない場合は、Notionのレスポンスから取得して付け加える
        task.append_id_and_url(task_id=response["id"], url=response["url"])
        return task

    def fetch_current_tasks(self) -> list["Task"]:
        response = self.api.get(path="tasks/current")
        return [Task.reconstruct(data=el) for el in response["data"]]

    # FIXME: いずれ消す。saveメソッドに統一できるはず
    def update_pomodoro_count(self, task: "Task") -> None:
        data = {
            "page_id": task.task_id,
        }
        self.api.post(path="page/pomodoro-count",
                          data=data) if not Environment.is_demo() else None


def _demo_save(task: Task) -> dict:
    return {
        "id": task.task_id or "afd886c4-ec90-40b1-9e9e-ba2536335ecc",
        "url": task.url or "https://www.notion.so/koboriakira/test-afd886c4ec9040b19e9eba2536335ecc",
    }
