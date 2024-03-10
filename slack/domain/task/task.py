from dataclasses import dataclass
from datetime import datetime as DatetimeObject


@dataclass(frozen=True)
class Task:
    title: str
    is_routine: bool = False
    description: str | None = None
    pomodoro_count: int = 0
    status: str | None = None
    start_date: DatetimeObject | None = None
    end_date: DatetimeObject | None = None
    # 以下はNotionページがあるときのフィールド
    task_id: str | None = None
    url: str | None = None
    mentioned_page_id: str | None = None

    @staticmethod
    def reconstruct(data: dict) -> "Task":
        """ データベースから取得したデータを元にTaskを再構築する"""
        return Task(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            is_routine=data["is_routine"],
            url=data["url"],
            status=data["status"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            mentioned_page_id=data["mentioned_page_id"],
            pomodoro_count=data["pomodoro_count"],
        )

    @staticmethod
    def from_title(title: str) -> "Task":
        is_routine = "【ルーティン】" in title
        return Task(title=title, is_routine=is_routine)

    def to_dict(self) -> dict:
        data = {}
        # Taskのフィールド変数のうち、Noneでないものを辞書に追加
        for field in self.__dataclass_fields__:
            if self.__dict__[field]:
                data[field] = self.__dict__[field]
        return data

    def increment_pomodoro_count(self) -> "Task":
        """ポモドーロカウンターをインクリメントする"""
        return Task(
            title=self.title,
            is_routine=self.is_routine,
            description=self.description,
            pomodoro_count=self.pomodoro_count + 1,
            status=self.status,
            start_date=self.start_date,
            end_date=self.end_date,
            task_id=self.task_id,
            url=self.url,
            mentioned_page_id=self.mentioned_page_id,
        )
