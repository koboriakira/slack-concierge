from domain.infrastructure.api.notion_api import NotionApi
from datetime import datetime as Datetime
from datetime import date as Date

class TaskGenerator:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api


    def add_to_inbox(self, title: str) -> dict:
        """ INBOXタスクに追加する """
        return self.notion_api.create_task(title=title)

    def add_scheduled_task(self, title: str, start_datetime: Datetime|Date) -> dict:
        """ INBOXタスクに追加する """
        return self.notion_api.create_task(title=title, start_date=start_datetime)
