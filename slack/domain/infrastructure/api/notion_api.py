from typing import Optional
from datetime import date as Date
from abc import ABCMeta, abstractmethod
from domain.notion.notion_page import RecipePage, NotionPage

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
                   ) -> list[NotionPage]:
        """ Notionのタスクを取得する """
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
