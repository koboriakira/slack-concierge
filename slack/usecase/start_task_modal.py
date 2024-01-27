from datetime import date as Date
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
import logging


class StartTaskModal:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api

    def handle(self, client: WebClient, trigger_id: str, callback_id: str):
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
