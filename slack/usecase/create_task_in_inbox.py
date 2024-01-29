from logging import Logger
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from usecase.service.slack_user_client import SlackUserClient
from domain.block import Blocks

class CreateTaskInInbox:
    def __init__(self, notion_api: NotionApi, client: WebClient, logger: Logger):
        self.notion_api = notion_api
        self.client = client
        self.logger = logger
        self.user_client = SlackUserClient()

    def handle(self, text: str, event_ts: str, thread_ts: str, channel: str):
        """ INBOXタスクを作成する """
        if event_ts == thread_ts:
            # スレッド開始の場合は、INBOXタスクとして新規起票する
            page = self.notion_api.create_task(title=text)
            self.user_client.handle(page_id=page["id"], channel=channel, thread_ts=thread_ts)
            return
        # スレッド返信の場合は、既存のINBOXタスクが親スレッドに書かれているので、それに対してブロックを追加する
        response = self.client.conversations_replies(channel=channel, ts=thread_ts)
        blocks = Blocks.from_values(response["messages"][0]["blocks"])
        page_id = blocks.get_context().page_id

        task = self.notion_api.find_task(task_id=page_id)
        self.notion_api.append_text_block(block_id=task.id, value=text)
