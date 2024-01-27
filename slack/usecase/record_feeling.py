from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder


class RecordFeeling:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.client = client

    def handle_modal(self, notion_page_block_id: str, channel: str, thread_ts: str, trigger_id: str, callback_id: str):
        """ 気持ちを記録するモーダルを表示する """
        block_builder = BlockBuilder()
        block_builder = block_builder.add_plain_text_input(
            action_id="feeling",
            label="気持ち",
            multiline=True,
        )
        block_builder = block_builder.add_context(
            {"channel_id": channel,
             "thread_ts": thread_ts,
             "block_id": notion_page_block_id}
        )

        blocks = block_builder.build()
        view_builder = ViewBuilder(callback_id=callback_id, blocks=blocks)
        view = view_builder.build()
        self.client.views_open(
            trigger_id=trigger_id,
            view=view,
        )

    def handle(self, block_id: str, feeling: str, channel: str, thread_ts: str):
        """ 気持ちを記録して、次回のポモドーロを開始できる状態にする """
        self.notion_api.append_feeling(page_id=block_id, feeling=feeling)

        block_builder = BlockBuilder()
        block_builder = block_builder.add_button_action(
            action_id="start-pomodoro",
            text="再開",
            value=block_id,
            style="primary",
        )
        block_builder = block_builder.add_button_action(
            action_id="complete-task",
            text="終了",
            value=block_id,
            style="danger",
        )
        block_builder = block_builder.add_context(
            {"channel_id": channel,
             "thread_ts": thread_ts}
        )
        blocks = block_builder.build()
        self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)
