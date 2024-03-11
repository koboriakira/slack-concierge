from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.task.task import Task


class TaskRepository(metaclass=ABCMeta):
    @abstractmethod
    def find_by_id(self, task_id: str) -> "Task":
        pass

    @abstractmethod
    def save(self, task: "Task") -> "Task":
        pass

    @abstractmethod
    def update_pomodoro_count(self, task: "Task") -> None:
        pass

    @abstractmethod
    def fetch_current_tasks(self) -> list["Task"]:
        pass
