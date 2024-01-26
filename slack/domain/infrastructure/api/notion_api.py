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
