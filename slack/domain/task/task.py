from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Task:
    title: str
    is_routine: bool = False
    description: str | None = None
    pomodoro_count: int = 0
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
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

    def increment_pomodoro_count(self) -> None:
        """ポモドーロカウンターをインクリメントする"""
        self.pomodoro_count += 1

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

    def append_id_and_url(self, task_id: str, url: str) -> None:
        """NotionページのIDとURLを追加する"""
        self.task_id = task_id
        self.url = url

    @staticmethod
    def test_instance() -> "Task":
        from slack.util.datetime import JST
        return Task(
            title="test",
            is_routine=False,
            description="test",
            pomodoro_count=3,
            status="ToDo",
            start_date=datetime(2024, 1, 1, tzinfo=JST),
            end_date=datetime(2024, 1, 1, tzinfo=JST),
            task_id="afd886c4-ec90-40b1-9e9e-ba2536335ecc",
            url="https://www.notion.so/koboriakira/test-afd886c4ec9040b19e9eba2536335ecc",
            mentioned_page_id=None,
        )
