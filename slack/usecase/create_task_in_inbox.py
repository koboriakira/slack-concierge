from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from logging import Logger

class CreateTaskInInbox:
    def __init__(self, notion_api: NotionApi, client: WebClient, logger: Logger):
        self.notion_api = notion_api
        self.client = client
        self.logger = logger

    def handle(self, text: str, event_ts: str, thread_ts: str, blocks: list[dict]):
        """ INBOXタスクを作成する """
        if event_ts == thread_ts:
            # スレッド開始の場合は、INBOXタスクとして新規起票する
            self.notion_api.create_task(title=text)
            return
        # スレッド返信の場合は、既存のINBOXタスクに対してブロックを追加する


if __name__ == "__main__":
    # python -m usecase.create_task_in_inbox
    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    import os
    notion_api = LambdaNotionApi()
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    usecase = CreateTaskInInbox(notion_api=notion_api, client=client)
    usecase.handle(text="テスト", event_ts="1706500982.880539", thread_ts="1706500982.880539")
