from typing import Optional
from datetime import date as Date
from datetime import datetime as Datetime
from abc import ABCMeta, abstractmethod
from domain.notion.notion_page import RecipePage, NotionPage, TaskPage

class NotionApi(metaclass=ABCMeta):
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
    def list_tasks(self,
                   start_date: Optional[Date] = None,
                   status: Optional[str] = None,
                   ) -> list[TaskPage]:
        """ Notionのタスクを取得する """
        pass

    @abstractmethod
    def list_current_tasks(self) -> list[TaskPage]:
        """ Notionの「やる予定」のタスクを取得する """
        pass

    @abstractmethod
    def find_task(self, task_id: str) -> TaskPage:
        """ Notionのタスクを1つ取得する """
        pass


    @abstractmethod
    def create_track_page(self, track_name: str,
                                artists: list[str],
                                spotify_url: Optional[str] = None,
                                cover_url: Optional[str] = None,
                                release_date: Optional[Date] = None,) -> dict:
        """ Notionに音楽のページを作成する """

    @abstractmethod
    def create_webclip_page(self,
                            url: str,
                            title: str,
                            summary: str,
                            tags: list[str],
                            text: str,
                            status: Optional[str] = None,
                            cover: Optional[str] = None,
                            ) -> dict:
        """ NotionにWebclipのページを作成する """
        pass

    @abstractmethod
    def create_video_page(self,
                            url: str,
                            title: str,
                            tags: list[str],
                            cover: Optional[str] = None,
                            ) -> dict:
        """ Notionに動画のページを作成する """
        pass

    @abstractmethod
    def add_book(
        self,
        google_book_id: Optional[str] = None,
        title: Optional[str] = None,) -> dict:
        """ Notionに本のページを作成する """
        pass

    @abstractmethod
    def create_prowrestling_page(self,
                                 url: str,
                                 title: str,
                                 date: Date,
                                 promotion: str,
                                 text: str,
                                 tags: list[str],
                                 cover: Optional[str] = None,
                                ) -> dict:
        """ Notionにプロレスのページを作成する """
        pass

    @abstractmethod
    def append_feeling(self,
                       page_id: str,
                       feeling: str,
                       ) -> dict:
        """ Notionのページの「気持ち」フィールドにテキストを追加 """
        pass

    @abstractmethod
    def update_pomodoro_count(self,
                              page_id: str,
                              count: Optional[int] = None,
                              ) -> dict:
        """ Notionのページの「ポモドーロカウンター」フィールドを更新 """
        pass

    @abstractmethod
    def update_status(self,
                              page_id: str,
                              value: str,
                              ) -> dict:
        """ Notionのページの「ステータス」フィールドを更新 """
        pass

    @abstractmethod
    def create_task(self,
                    title: Optional[str] = None,
                    mentioned_page_id: Optional[str] = None,
                    start_date: Optional[Date|Datetime] = None,
                    end_date: Optional[Date|Datetime] = None,
                    ) -> dict:
        """ タスクページを新規作成する """
        pass

    @abstractmethod
    def append_text_block(self,
                          block_id: str,
                          value: str,
                          ) -> dict:
        """ テキストブロックを追加する """
        pass
