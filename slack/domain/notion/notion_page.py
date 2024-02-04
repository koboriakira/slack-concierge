import json
from typing import Optional
from datetime import date as DateObject
from datetime import datetime as DatetimeObject


class NotionPage:
    id: str
    url: str
    title: str

    def __init__(self, id: str, url: str, title: str):
        self.id = id
        self.url = url
        self.title = title

    def dump(self) -> str:
        return json.dumps({
            "id": self.id,
            "url": self.url,
            "title": self.title
        }, ensure_ascii=False)

    def load(json_str: str) -> "NotionPage":
        json_dict = json.loads(json_str)
        return NotionPage(
            id=json_dict["id"],
            url=json_dict["url"],
            title=json_dict["title"]
        )

    def from_dict(params: dict) -> "NotionPage":
        return NotionPage(
            id=params["id"],
            url=params["url"],
            title=params["title"]
        )

    @property
    def link_text(self) -> str:
        return f"<{self.url}|{self.title}>"


class ProjectPage(NotionPage):
    status: str

    def __init__(self, id: str, url: str, title: str, status: str):
        super().__init__(id, url, title)
        self.status = status

    def from_dict(params: dict) -> "ProjectPage":
        return ProjectPage(
            id=params["id"],
            url=params["url"],
            title=params["title"],
            status=params["status"]
        )


class RecipePage(NotionPage):
    status: str

    def __init__(self, id: str, url: str, title: str, ingredients: list[str], meal_categories: list[str], status: str):
        super().__init__(id, url, title)
        self.ingredients = ingredients
        self.meal_categories = meal_categories
        self.status = status

    def from_dict(params: dict) -> "RecipePage":
        return RecipePage(
            id=params["id"],
            url=params["url"],
            title=params["title"],
            ingredients=params["ingredients"],
            meal_categories=params["meal_categories"],
            status=params["status"],
        )

class TaskPage(NotionPage):
    status: str
    feeling: str
    start_date: Optional[DatetimeObject] = None
    end_date: Optional[DatetimeObject] = None
    task_kind: Optional[str] = None

    def __init__(self, id: str, url: str, title: str, status: str, feeling: str, start_date: Optional[str] = None, end_date: Optional[str] = None, task_kind: Optional[str] = None):
        super().__init__(id, url, title)
        self.status = status
        self.feeling = feeling
        self.start_date = start_date
        self.end_date = end_date
        self.task_kind = task_kind

    def from_dict(params: dict) -> "TaskPage":
        return TaskPage(
            id=params["id"],
            url=params["url"],
            title=params["title"],
            status=params["status"],
            feeling=params["feeling"],
            start_date=DatetimeObject.fromisoformat(params["start_date"]) if params["start_date"] else None,
            end_date=DatetimeObject.fromisoformat(params["end_date"]) if params["end_date"] else None,
            task_kind=params["task_kind"] if "task_kind" in params else None,
        )

    def title_within_50_chars(self) -> str:
        if len(self.title) <= 50:
            return self.title
        return self.title[:50] + "..."

    @property
    def is_routine(self) -> bool:
        return self.title.startswith("【ルーティン】")
