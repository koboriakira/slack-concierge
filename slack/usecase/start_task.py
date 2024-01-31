from datetime import date as Date
from typing import Optional
import logging
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from util.environment import Environment
from domain.channel import ChannelType
from util.cache import Cache
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService

ROUTINE_TASK_OPTIONS = [
    {"家事": "housework"},
    {"料理": "cooking"},
    {"買い物": "shopping"},
    {"朝食": "breakfast"},
    {"昼食": "lunch"},
    {"夕食": "dinner"},
    {"入浴": "bath"},
    {"睡眠": "sleep"},
    {"日次レビュー": "daily-review"}, # Notionの更新ページ確認、Googleカレンダーの実績確認、Inbox整理、TODAYタスクの決定
    {"週次レビュー": "weekly-review"},
    {"月次レビュー": "monthly-review"},
    {"その他": "other"},
]

TODAY_TASK_OPTIONS = "today_task_options"

class StartTask:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.client = client
        self.scheduler_service = EventBridgeSchedulerService()

    def handle_modal(self, client: WebClient, trigger_id: str, callback_id: str):
        """ 最初のタスク選択のモーダルを表示する """
        today = Date.today()
        block_builder = BlockBuilder()

        # タスクの選択肢を作成する。今日の未了タスクが対象
        task_options = Cache.get(TODAY_TASK_OPTIONS)
        if task_options is None:
            tasks = self.notion_api.list_tasks(start_date=today, status="ToDo,InProgress")
            # タイトルが無題のものは除外する
            tasks = [t for t in tasks if t.title != ""]
            task_options = [{
                "text": t.title,
                "value": t.id
            } for t in tasks]
            Cache.set(TODAY_TASK_OPTIONS, task_options)

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
            options=[{"text": k, "value": v} for d in ROUTINE_TASK_OPTIONS for k, v in d.items()],
            optional=True,
        )

        blocks = block_builder.build()
        logging.debug(blocks)

        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        client.views_open(
            trigger_id=trigger_id,
            view=view,
        )

    def handle_prepare(self, task_id: Optional[str], task_title: str) -> dict:
        """
        ポモドーロ開始ボタンを投稿して、タスクを開始できる状態にする
        task_idが未指定の場合は、新規タスクとして起票する
        """
        if task_id is None:
            page = self.notion_api.create_task(title=task_title, start_date=Date.today())
            task_id = page["id"]

        channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST
        task_url = f"https://www.notion.so/{task_id.replace('-', '')}"
        text = f"<{task_url}|{task_title}>"
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(text=text)
        block_builder = block_builder.add_context({"page_id": task_id})
        blocks = block_builder.build()

        response = self.client.chat_postMessage(text=text, channel=channel.value, blocks=blocks)

        self.scheduler_service.set_pomodoro_timer(
            page_id=task_id,
            channel=channel.value,
            thread_ts=response["ts"],
        )

        return {
            "thread_ts": response["ts"],
            "page_id": task_id,
        }
