from abc import ABCMeta, abstractmethod
from datetime import date as Date
from datetime import datetime as Datetime

from domain.notion.notion_page import NotionPage, RecipePage, TaskPage


class NotionApi(metaclass=ABCMeta):
    @abstractmethod
    def post(self, path: str, data: dict) -> dict:
        """NotionAPIにPOSTリクエストを送る。共通化のために作成"""

    @abstractmethod
    def get(self, path: str, params: dict | None = None) -> dict:
        """NotionAPIにGETリクエストを送る。共通化のために作成"""

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
        start_date: Date | None = None,
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
        release_date: Date | None = None,
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
        date: Date,
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
        start_date: Date | Datetime | None = None,
        end_date: Date | Datetime | None = None,
    ) -> dict:
        """タスクページを新規作成する"""

    @abstractmethod
    def append_text_block(
        self,
        block_id: str,
        value: str,
    ) -> dict:
        """テキストブロックを追加する"""
