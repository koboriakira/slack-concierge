from abc import ABCMeta, abstractmethod
from domain.notion.notion_page import RecipePage

class NotionApi(metaclass=ABCMeta):
    @abstractmethod
    def list_recipes(self) -> list[RecipePage]:
        pass
