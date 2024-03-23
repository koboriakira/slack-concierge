from dataclasses import dataclass

from domain.task.task import Task


@dataclass
class CreateTaskRequest:
    title: str | None = None
    mentioned_page_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    task_kind: str | None = None

    @staticmethod
    def from_entity(entity: Task) -> "CreateTaskRequest":
        return CreateTaskRequest(
            title=entity.title,
            mentioned_page_id=entity.mentioned_page_id,
            start_date=entity.start_date.isoformat() if entity.start_date else None,
            end_date=entity.end_date.isoformat() if entity.end_date else None,
            status=entity.status,
            task_kind=entity.task_kind,
        )
