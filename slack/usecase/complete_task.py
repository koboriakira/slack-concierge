from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi


class CompleteTask:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.client = client

    def handle(self, block_id: str, channel: str, thread_ts: str):
        """ タスクを完了する """
        # ステータスを更新
        self.notion_api.update_status(page_id=block_id, value="Done")
        self.client.chat_postMessage(text="タスクを完了しました！", channel=channel, thread_ts=thread_ts)
