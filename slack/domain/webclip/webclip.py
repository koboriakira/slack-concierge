from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from domain.infrastructure.api.notion_api import NotionApi


@dataclass
class Webclip:
    title: str
    url: str
    thumb_url: str | None = None
    notion_page_id: str | None = None
    notion_page_url: str | None = None

    @staticmethod
    def from_attachment(url: str, attachment: dict) -> "Webclip":
        return Webclip(
            title=attachment["title"],
            url=url,
            thumb_url=attachment.get("image_url") or attachment.get("thumb_url"),
        )


class WebclipRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_from_attachment(self, url: str, attachment:dict) -> Webclip:
        pass

class NotionWebclipRepository(WebclipRepository):
    def __init__(self, notion_api: NotionApi|None = None) -> None:
        from infrastructure.api.lambda_notion_api import LambdaNotionApi
        self.notion_api = notion_api or LambdaNotionApi()

    def save_from_attachment(self, url: str, attachment:dict) -> Webclip:
        webclip = Webclip.from_attachment(url=url, attachment=attachment)
        data = {
            "url": webclip.url,
            "title": webclip.title,
        }
        if webclip.thumb_url:
            data["cover"] = webclip.thumb_url
        response = self.notion_api.post(path="webclip", data=data)
        webclip.notion_page_id = response["id"]
        webclip.notion_page_url = response["url"]
        return webclip
