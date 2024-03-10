
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
        data = response
        return task.add_id_and_url(task_id=data["id"], url=data["url"])

    def update_pomodoro_count(self, task: "Task") -> "Task":
        data = {
            "page_id": task.task_id,
        }
        _ = self.api.post(url="page/pomodoro-count",
                          data=data) if not Environment.is_demo() else None
        return task.increment_pomodoro_count()

def _demo_save(task: Task) -> dict:
    return {
        "id": task.task_id or "afd886c4-ec90-40b1-9e9e-ba2536335ecc",
        "url": task.url or "https://www.notion.so/koboriakira/test-afd886c4ec9040b19e9eba2536335ecc",
    }
