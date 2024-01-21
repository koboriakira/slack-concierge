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
