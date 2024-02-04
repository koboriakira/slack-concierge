from domain.infrastructure.api.notion_api import NotionApi

class TaskGenerator:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api


    def add_to_inbox(self, title: str) -> dict:
        """ INBOXタスクに追加する """
        return self.notion_api.create_task(title=title)
