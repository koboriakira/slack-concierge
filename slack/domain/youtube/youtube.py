from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from domain.channel.thread import Thread
from domain.infrastructure.api.notion_api import NotionApi


@dataclass
class Youtube:
    title: str
    url: str
    channel_name: str | None = None
    thumb_url: str | None = None
    notion_page_id: str | None = None
    notion_page_url: str | None = None

    @staticmethod
    def from_attachment(url: str, attachment: dict) -> "Youtube":
        return Youtube(
            title=attachment["title"],
            url=url,
            channel_name=attachment.get("author_name"),
            thumb_url=attachment.get("thumb_url"),
        )


class YoutubeRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_from_attachment(self, url: str, attachment:dict, slack_thread: Thread|None = None) -> Youtube:
        pass

class NotionYoutubeRepository(YoutubeRepository):
    def __init__(self, notion_api: NotionApi|None = None) -> None:
        from infrastructure.api.lambda_notion_api import LambdaNotionApi
        self.notion_api = notion_api or LambdaNotionApi()

    def save_from_attachment(self, url: str, attachment:dict, slack_thread: Thread|None = None) -> Youtube:
        youtube = Youtube.from_attachment(url=url, attachment=attachment)
        title = youtube.title
        if youtube.channel_name:
            title += " | " + youtube.channel_name
        data = {
            "url": youtube.url,
            "title": title,
        }
        if youtube.thumb_url:
            data["cover"] = youtube.thumb_url
        if slack_thread:
            data["slack_channel"] = slack_thread.channel_id
            data["slack_thread_ts"] = slack_thread.thread_ts
        response = self.notion_api.post(path="video", data=data)
        youtube.notion_page_id = response["id"]
        youtube.notion_page_url = response["url"]
        return youtube
