from dataclasses import dataclass

from domain.task.task import Task


@dataclass
class UpdateTaskRequest:
    status: str

    @staticmethod
    def from_entity(entity: Task) -> "UpdateTaskRequest":
        return UpdateTaskRequest(status=entity.status)

