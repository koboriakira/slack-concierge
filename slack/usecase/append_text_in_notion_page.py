from domain.infrastructure.api.notion_api import NotionApi

class AppendTextInNotionPage:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api


    def handle(self, text: str, page_id: str):
        self.notion_api.append_text_block(block_id=page_id, value=text)
