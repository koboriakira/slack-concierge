from domain.infrastructure.api.notion_api import NotionApi

class CreateTask:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api


    def handle(self, text: str):
        """ タスクを作成する """
        page = self.notion_api.create_task(title=text if "\n" not in text else text.split("\n")[0])
