from dataclasses import dataclass

from domain.task.task import Task


@dataclass
class UpdateTaskRequest:
    status: str|None
    pomodoro_count: int|None

    @staticmethod
    def from_entity(entity: Task) -> "UpdateTaskRequest":
        return UpdateTaskRequest(
            status=entity.status if entity.status else None,
            pomodoro_count=entity.pomodoro_count,
        )
