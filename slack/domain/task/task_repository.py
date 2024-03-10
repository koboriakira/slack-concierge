from abc import ABCMeta, abstractmethod

from domain.task.task import Task


class TaskRepository(metaclass=ABCMeta):
    @abstractmethod
    def find_by_id(self, task_id: str) -> "Task":
        pass

    @abstractmethod
    def save(self, task: "Task") -> "Task":
        pass

    @abstractmethod
    def update_pomodoro_count(self, task: "Task") -> "Task":
        pass

# あとでinfra層に実装を移す
class NotionTaskRepository(TaskRepository):
    def __init__(self) -> None:
        import os

        from infrastructure.api.lambda_notion_api import LambdaNotionApi
        self.domain = os.environ["LAMBDA_NOTION_API_DOMAIN"]
        self.api = LambdaNotionApi()

    def find_by_id(self, task_id: str) -> "Task":
        response = self.api._get(path=f"task/{task_id}")
        return Task.reconstruct(data=response["data"])

    def save(self, task: "Task") -> "Task":
        # FIXME: postってパスじゃなくてURLだった。直しておこう
        response = self.api._post(url=f"{self.domain}task", data=task.to_dict())
        data = response
        return task.add_id_and_url(task_id=data["id"], url=data["url"])

    def update_pomodoro_count(self, task: "Task") -> "Task":
        api_url = f"{self.domain}page/pomodoro-count"
        data = {
            "page_id": task.task_id,
        }
        _ = self.api._post(url=api_url, data=data)
        return task.increment_pomodoro_count()
