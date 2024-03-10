import logging
from datetime import datetime as Datetime
from datetime import timedelta

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.infrastructure.api.notion_api import NotionApi
from domain.routine.routine_task import RoutineTask
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from infrastructure.repository.current_tasks_s3_repository import CurrentTasksS3Repository
from util.datetime import now
from util.environment import Environment

ROUTINE_TASK_OPTIONS = [
    {"text": task.value, "value": task.name} for task in RoutineTask
]

TODAY_TASK_OPTIONS = "today_task_options"


class StartTask:
    def __init__(self, notion_api: NotionApi, client: WebClient) -> None:
        self.notion_api = notion_api
        self.client = client
        self.current_tasks_s3_repository = CurrentTasksS3Repository()

    def handle_modal(self, client: WebClient, trigger_id: str, callback_id: str):
        """最初のタスク選択のモーダルを表示する"""
        block_builder = BlockBuilder()

        # タスクの選択肢を作成する。今日の未了タスクが対象
        current_tasks_cache = self.current_tasks_s3_repository.load()
        if current_tasks_cache is None or Datetime.fromisoformat(current_tasks_cache["expires_at"]) < now() or Environment.is_dev():
            tasks = self.notion_api.list_current_tasks()
            task_options = [
                {"text": t.title_within_50_chars(), "value": t.id} for t in tasks if t.title != ""
            ]
            expires_at = now() + timedelta(minutes=5)
            current_tasks_cache = {
                "task_options": task_options,
                "expires_at": expires_at.isoformat(),
            }
            self.current_tasks_s3_repository.save(current_tasks_cache)

        task_options = current_tasks_cache.get("task_options", [])
        if len(task_options) > 0:
            block_builder = block_builder.add_static_select(
                action_id="task",
                options=task_options,
                optional=True,
            )
        block_builder = block_builder.add_plain_text_input(
            action_id="new-task",
            label="タスクを起票して開始する場合",
            optional=True,
        )
        block_builder = block_builder.add_static_select(
            action_id="routine-task",
            label="ルーチンタスクを開始する場合",
            options=ROUTINE_TASK_OPTIONS,
            optional=True,
        )

        blocks = block_builder.build()
        logging.debug(blocks)

        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        client.views_open(
            trigger_id=trigger_id,
            view=view,
        )

    def handle_prepare(self, task_title: str, task_id: str | None = None) -> dict:
        """
        ポモドーロ開始ボタンを投稿して、タスクを開始できる状態にする
        task_idが未指定の場合は、新規タスクとして起票する
        """
        if task_id is None:
            page = self.notion_api.create_task(
                title=task_title, start_date=now().date(),
            )
            task_id = page["id"]

        channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST
        task_url = f"https://www.notion.so/{task_id.replace('-', '')}"
        text = f"<{task_url}|{task_title}>"
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(text=text)
        if "【ルーティン】" in task_title:
            routine_task = RoutineTask.from_name(task_title)
            if routine_task.description is not None:
                block_builder = block_builder.add_section(text=routine_task.description)
        block_builder = block_builder.add_button_action(
            action_id="complete-task",
            text="終了",
            value=task_id,
            style="danger",
        )
        block_builder = block_builder.add_context({"page_id": task_id})
        blocks = block_builder.build()

        response = self.client.chat_postMessage(
            text=text, channel=channel.value, blocks=blocks,
        )

        return {
            "thread_ts": response["ts"],
            "page_id": task_id,
        }
