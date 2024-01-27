from datetime import date as Date
import logging
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from util.environment import Environment


class StartPomodoro:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.client = client

    def handle(self, notion_page_block_id: str, channel: str, thread_ts: str):
        """ ポモドーロの開始を通達する """
        # 開始を連絡
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"開始しました！"
        )
        blocks = block_builder.build()
        self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)

        # ポモドーロカウンターをインクリメント
        self.notion_api.update_pomodoro_count(page_id=notion_page_block_id)

        # TODO: 25分後に終了を通知したい。EventBridgeなどを使う必要がありそうで時間がかかるので、
        # とりあえず開始直後に通知するようにしておいて、机上のタイマーで測っておく
        # そのため以下はEventBridge実装後に移行する
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"25分が経過しました！\n「気持ち」を記録して休憩してください"
        )
        block_builder = block_builder.add_button_action(
            action_id="record-feeling",
            text="気持ちを記録",
            value=notion_page_block_id,
            style="primary",
        )
        blocks = block_builder.build()
        self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)
