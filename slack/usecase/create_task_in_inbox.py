from logging import Logger
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi

class CreateTaskInInbox:
    def __init__(self, notion_api: NotionApi, client: WebClient, logger: Logger):
        self.notion_api = notion_api
        self.client = client
        self.logger = logger

    def handle(self, text: str, event_ts: str, thread_ts: str, channel: str):
        """ INBOXタスクを作成する """
        if event_ts == thread_ts:
            # スレッド開始の場合は、INBOXタスクとして新規起票する
            self.notion_api.create_task(title=text)
            return
        # スレッド返信の場合は、既存のINBOXタスクに対してブロックを追加する

        # まずスレッドの親メッセージのtextを取得する。これがタスクのタイトルであるはず
        response = self.client.conversations_replies(channel=channel, ts=thread_ts)
        task_title = response["messages"][0]["text"]

        tasks = self.notion_api.list_tasks(status="todo,inprogress")
        for task in tasks:
            if task.title == task_title:
                self.notion_api.append_text_block(block_id=task.id, value=text)
