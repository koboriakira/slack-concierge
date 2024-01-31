from logging import Logger
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from usecase.service.slack_user_client import SlackUserClient

class CreateTaskInInbox:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api
        self.user_client = SlackUserClient()

    def handle(self, text: str, event_ts: str, channel: str):
        """ INBOXタスクを作成する """
        page = self.notion_api.create_task(title=text if "\n" not in text else text.split("\n")[0])
        self.user_client.handle(page_id=page["id"], channel=channel, thread_ts=event_ts)
