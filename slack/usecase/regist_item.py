from datetime import date as Date
from typing import Optional
import re
import logging
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from util.environment import Environment
from domain.channel import ChannelType
from util.cache import Cache
from domain.routine.routine_task import RoutineTask
from usecase.service.task_generator import TaskGenerator

ROUTINE_TASK_OPTIONS = [{
        "text": task.value,
        "value": task.name
    } for task in RoutineTask]

CATEGORY_OPTIONS = [
    {
        "text": "書籍",
        "value": "book",
    }
]

class RegistItem:
    def __init__(self, notion_api: NotionApi, client: WebClient):
        self.notion_api = notion_api
        self.task_generator = TaskGenerator(notion_api=notion_api)
        self.client = client

    def handle_modal(self, client: WebClient, trigger_id: str, callback_id: str):
        """ 最初のタスク選択のモーダルを表示する """
        today = Date.today()
        block_builder = BlockBuilder()

        # 登録するカテゴリ。いまは本一択
        block_builder = block_builder.add_static_select(
            action_id="category",
            options=CATEGORY_OPTIONS,
        )
        # 本の情報
        block_builder = block_builder.add_plain_text_input(
            action_id="book-info",
            label="GoogleブックスのIDもしくは書籍名",
            optional=True,
        )

        blocks = block_builder.build()
        logging.debug(blocks)

        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        client.views_open(
            trigger_id=trigger_id,
            view=view,
        )

    def regist_book(self, book_info: str) -> dict:
        """
        ポモドーロ開始ボタンを投稿して、タスクを開始できる状態にする
        task_idが未指定の場合は、新規タスクとして起票する
        """
        google_book_id, title = _get_google_book_id_or_title(book_info)
        book = self.notion_api.add_book(google_book_id=google_book_id, title=title)
        page_id = book["id"]
        page_url = book["url"]
        self.task_generator.add_to_inbox_by_page_id(page_id=page_id)
        self.client.chat_postMessage(text=f"書籍を登録しました: {page_url}", channel=ChannelType.DIARY.value)
        return book

def _get_google_book_id_or_title(book_info: str) -> tuple[Optional[str], Optional[str]]:
    """ Google BooksのIDかタイトルを返す """
    if re.match(r"[_\-A-Za-z0-9]{10,}", book_info):
        return book_info, None
    else:
        return None, book_info

if __name__ == "__main__":
    # python -m usecase.regist_item
    print(_get_google_book_id_or_title("BB__vQAACAAJ"))
    print(_get_google_book_id_or_title("大切なことだけをやりなさい"))
