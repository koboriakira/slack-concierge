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
            task_id=data["id"],
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

    def create_slack_message_start_task(self) -> tuple[str, list[dict]]:
        from slack.domain_service.block.block_builder import BlockBuilder
        """タスク開始時のSlackメッセージを生成する"""
        text = f"<{self.url}|{self.title}>"
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(text=text)
        block_builder = block_builder.add_button_action(
            action_id="complete-task",
            text="終了",
            value=self.task_id,
            style="danger",
        )
        block_builder = block_builder.add_context({"page_id": self.task_id})
        blocks = block_builder.build()
        return text, blocks

    def add_id_and_url(self, task_id: str, url: str) -> "Task":
        """NotionページのIDとURLを追加したTaskを返す"""
        return Task(
            title=self.title,
            is_routine=self.is_routine,
            description=self.description,
            pomodoro_count=self.pomodoro_count,
            status=self.status,
            start_date=self.start_date,
            end_date=self.end_date,
            task_id=task_id,
            url=url,
            mentioned_page_id=self.mentioned_page_id,
        )
