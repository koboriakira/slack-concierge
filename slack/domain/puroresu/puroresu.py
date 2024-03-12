from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import date

import requests

from domain.infrastructure.api.notion_api import NotionApi


@dataclass
class Puroresu:
    title: str
    url: str
    thumb_url: str | None = None
    match_date: date | None = None
    promotion: str | None = None
    venue: str | None = None
    description: str | None = None
    notion_page_id: str | None = None
    notion_page_url: str | None = None

    @staticmethod
    def create_from_wrestle_universe(url: str) -> "Puroresu":
        # WUのAPI経由でデータを取得する
        event_id = url.split("/")[-1]
        # event_url = f"https://api.wrestle-universe.com/v1/events/{event_id}?al=ja"
        api_url = f"https://api.wrestle-universe.com/v1/videoEpisodes/{event_id}?al=ja"
        response = requests.get(api_url, timeout=10)
        data:dict = response.json()

        return Puroresu(
            url=url,
            title=data["displayName"],
            thumb_url=data.get("keyVisualUrl"),
            match_date=date.fromisoformat(data["labels"]["matchDate"].split("T")[0]),
            promotion=get_promotion_name(data["labels"]["group"]),
            venue=data["labels"].get("venue"),
            description=data.get("description"),
        )


class PuroresuRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, puroresu: Puroresu) -> bool:
        pass

class NotionProRepository(PuroresuRepository):
    def __init__(self, notion_api: NotionApi|None = None) -> None:
        from infrastructure.api.lambda_notion_api import LambdaNotionApi
        self.notion_api = notion_api or LambdaNotionApi()

    def save(self, puroresu: Puroresu) -> bool:  # noqa: C901
        tags = []
        data = {
            "url": puroresu.url,
            "title": puroresu.title,
        }
        if puroresu.thumb_url:
            data["cover"] = puroresu.thumb_url
        if puroresu.match_date:
            data["date"] = puroresu.match_date.isoformat()
        if puroresu.promotion:
            data["promotion"] = puroresu.promotion
            tags.append(puroresu.promotion)
        if puroresu.description:
            data["text"] = puroresu.description
        if puroresu.venue:
            tags.append(puroresu.venue)
        if tags:
            data["tags"] = tags

        return True

def get_promotion_name(group_key: str) -> str:
    match group_key:
        case "tjpw":
            return "東京女子プロレス"
        case _:
            return group_key
