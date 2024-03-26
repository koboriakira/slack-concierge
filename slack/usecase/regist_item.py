import re

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder

CATEGORY_OPTIONS = [
    {
        "text": "書籍",
        "value": "book",
    },
]

class RegistItemModalUseCase:
    def __init__(self, slack_client: WebClient) -> None:
        self._slack_client = slack_client

    def execute(self, trigger_id: str, callback_id: str) -> None:
        """ 最初のタスク選択のモーダルを表示する """
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
        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        self._slack_client.views_open(
            trigger_id=trigger_id,
            view=view,
        )

class RegistItemUseCase:
    def __init__(self, notion_api: NotionApi) -> None:
        self.notion_api = notion_api

    def regist_book(self, book_info: str) -> None:
        """
        ポモドーロ開始ボタンを投稿して、タスクを開始できる状態にする
        task_idが未指定の場合は、新規タスクとして起票する
        """
        google_book_id, title = self._get_google_book_id_or_title(book_info)
        self.notion_api.add_book(
            google_book_id=google_book_id,
            title=title,
            slack_channel=ChannelType.DIARY.value)

    def _get_google_book_id_or_title(self, book_info: str) -> tuple[str | None, str | None]:
        """ Google BooksのIDかタイトルを返す """
        if re.match(r"[_\-A-Za-z0-9]{10,}", book_info):
            return book_info, None
        return None, book_info
