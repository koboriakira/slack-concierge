import json
from abc import ABCMeta, abstractmethod
from datetime import date, datetime

from domain.notion.notion_page import NotionPage, RecipePage, TaskPage


class NotionApiError(Exception):
    def __init__(self, status_code: int, message: str, params: dict | None = None) -> None:
        self.status_code = status_code
        self.message = message
        self.params = params or {}
        super().__init__(
            f"status_code: {status_code}, message: {message}, params: {json.dumps(self.params, ensure_ascii=False)}"
        )


class NotionApi(metaclass=ABCMeta):
    @abstractmethod
    def post(self, path: str, data: dict) -> dict:
        """
        NotionAPIにPOSTリクエストを送る。共通化のために作成

        Args:
            path (str): リクエストパス
            data (dict): 送信データ

        Returns:
            dict: レスポンスデータ

        Raises:
            NotionApiError: NotionAPIからエラーレスポンスが返ってきた場合
        """

    @abstractmethod
    def get(self, path: str, params: dict | None = None) -> dict:
        """
        NotionAPIにGETリクエストを送る。共通化のために作成

        Args:
            path (str): リクエストパス
            params (dict, optional): クエリパラメータ. Defaults to None.

        Returns:
            dict: レスポンスデータ

        Raises:
            NotionApiError: NotionAPIからエラーレスポンスが返ってきた場合
        """

    @abstractmethod
    def list_recipes(self) -> list[RecipePage]:
        pass

    @abstractmethod
    def list_projects(self) -> list[NotionPage]:
        pass

    @abstractmethod
    def find_project(self, project_id: str) -> NotionPage:
        pass

    @abstractmethod
    def list_tasks(
        self,
        start_date: date | None = None,
        status: str | None = None,
    ) -> list[TaskPage]:
        """Notionのタスクを取得する"""

    @abstractmethod
    def list_current_tasks(self) -> list[TaskPage]:
        """Notionの「やる予定」のタスクを取得する"""

    @abstractmethod
    def find_task(self, task_id: str) -> TaskPage:
        """Notionのタスクを1つ取得する"""

    @abstractmethod
    def create_track_page(
        self,
        track_name: str,
        artists: list[str],
        spotify_url: str | None = None,
        cover_url: str | None = None,
        release_date: date | None = None,
    ) -> dict:
        """Notionに音楽のページを作成する"""

    @abstractmethod
    def create_webclip_page(
        self,
        url: str,
        title: str,
        cover: str | None = None,
    ) -> dict:
        """NotionにWebclipのページを作成する"""

    @abstractmethod
    def create_video_page(
        self,
        url: str,
        title: str,
        tags: list[str],
        cover: str | None = None,
    ) -> dict:
        """Notionに動画のページを作成する"""

    @abstractmethod
    def add_book(
        self,
        google_book_id: str | None = None,
        title: str | None = None,
        slack_channel: str | None = None,
    ) -> dict:
        """Notionに本のページを作成する"""

    @abstractmethod
    def create_prowrestling_page(
        self,
        url: str,
        title: str,
        date: date,
        promotion: str,
        text: str,
        tags: list[str],
        cover: str | None = None,
    ) -> dict:
        """Notionにプロレスのページを作成する"""

    @abstractmethod
    def append_feeling(
        self,
        page_id: str,
        feeling: str,
    ) -> dict:
        """Notionのページの「気持ち」フィールドにテキストを追加"""

    @abstractmethod
    def update_pomodoro_count(
        self,
        page_id: str,
        count: int | None = None,
    ) -> dict:
        """Notionのページの「ポモドーロカウンター」フィールドを更新"""

    @abstractmethod
    def update_status(
        self,
        page_id: str,
        value: str,
    ) -> dict:
        """Notionのページの「ステータス」フィールドを更新"""

    @abstractmethod
    def create_task(
        self,
        title: str | None = None,
        mentioned_page_id: str | None = None,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> dict:
        """タスクページを新規作成する"""

    @abstractmethod
    def append_text_block(
        self,
        block_id: str,
        value: str,
    ) -> dict:
        """テキストブロックを追加する"""
