from datetime import date as Date
import logging
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from util.environment import Environment
from domain.channel import ChannelType


class StartTask:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.client = client

    def handle_modal(self, client: WebClient, trigger_id: str, callback_id: str):
        """ 最初のタスク選択のモーダルを表示する """
        today = Date.today()
        block_builder = BlockBuilder()

        # タスクの選択肢を作成する。今日の未了タスクが対象
        tasks = self.notion_api.list_tasks(start_date=today, status="ToDo,InProgress")
        # タイトルが無題のものは除外する
        tasks = [t for t in tasks if t.title != ""]
        task_options = [{
            "text": t.title,
            "value": t.id
        } for t in tasks]
        block_builder = block_builder.add_static_select(
            action_id="task",
            options=task_options,
        )

        blocks = block_builder.build()
        logging.debug(blocks)

        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        client.views_open(
            trigger_id=trigger_id,
            view=view,
        )

    def handle_prepare(self, task_id: str, task_title: str):
        """ ポモドーロ開始ボタンを投稿して、タスクを開始できる状態にする """
        task_url = f"https://www.notion.so/{task_id.replace('-', '')}"
        text = f"<{task_url}|{task_title}> を開始します"
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=text,
        )
        block_builder = block_builder.add_button_action(
            action_id="start-pomodoro",
            text="開始",
            value=task_id,
            style="primary",
        )
        blocks = block_builder.build()
        channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST

        self.client.chat_postMessage(text=text, blocks=blocks, channel=channel.value)
