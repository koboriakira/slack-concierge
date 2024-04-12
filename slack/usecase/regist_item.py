import re
from enum import Enum

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder


class RegistCategory(Enum):
    BOOK = "書籍"
    RECIPE = "レシピ"

    def to_option(self) -> dict:
        return {"text": self.value, "value": self.name}


class RegistItemModalUseCase:
    def __init__(self, slack_client: WebClient) -> None:
        self._slack_client = slack_client

    def execute(self, trigger_id: str, callback_id: str) -> None:
        """最初のタスク選択のモーダルを表示する"""
        block_builder = BlockBuilder()

        # 登録するカテゴリ
        block_builder = block_builder.add_static_select(
            action_id="category",
            options=[c.to_option() for c in RegistCategory],
        )

        # 本の情報
        block_builder = block_builder.add_plain_text_input(
            action_id="book-info",
            label="GoogleブックスのIDもしくは書籍名",
            optional=True,
        )

        # レシピのURL、詳細
        block_builder = block_builder.add_plain_text_input(
            action_id="recipe-url",
            label="レシピのURL",
            optional=True,
        )
        block_builder = block_builder.add_plain_text_input(
            action_id="recipi-desc",
            label="レシピの詳細",
            multiline=True,
            optional=True,
        )

        blocks = block_builder.build()
        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        self._slack_client.views_open(
            trigger_id=trigger_id,
            view=view,
        )


class RegistBookUseCase:
    def __init__(self, notion_api: NotionApi) -> None:
        self.notion_api = notion_api

    def regist_book(self, book_info: str) -> None:
        """
        書籍を登録する
        """
        google_book_id, title = self._get_google_book_id_or_title(book_info)
        self.notion_api.add_book(google_book_id=google_book_id, title=title, slack_channel=ChannelType.DIARY.value)

    def _get_google_book_id_or_title(self, book_info: str) -> tuple[str | None, str | None]:
        """Google BooksのIDかタイトルを返す"""
        if re.match(r"[_\-A-Za-z0-9]{10,}", book_info):
            return book_info, None
        return None, book_info


class RegistRecipeUseCase:
    def __init__(self, notion_api: NotionApi) -> None:
        self._notion_api = notion_api

    def regist_recipe(self, recipe_url: str, recipe_desc: str) -> None:
        """
        書籍を登録する
        """
        data = {
            "description": recipe_desc,
            "reference_url": recipe_url,
            "slack_channel": ChannelType.DIARY.value,
        }
        _result = self._notion_api.post(path="recipes", data=data)
        print(_result)
