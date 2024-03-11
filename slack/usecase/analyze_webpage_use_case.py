import json
import logging
from dataclasses import dataclass
from datetime import date as Date
from enum import IntEnum

import requests
from slack_sdk.web import WebClient

from domain.infrastructure.api.notion_api import NotionApi
from domain.youtube.youtube import NotionYoutubeRepository, YoutubeRepository


class SiteType(IntEnum):
    TWITTER = 1
    YOUTUBE = 2
    WRESTLE_UNIVERSE = 3
    DEFAULT = 99

    @staticmethod
    def from_url(url: str) -> "SiteType":
        if "x.com" in url:
            return SiteType.TWITTER
        if "youtube.com" in url:
            return SiteType.YOUTUBE
        if "wrestle-universe.com" in url:
            return SiteType.WRESTLE_UNIVERSE
        return SiteType.DEFAULT


@dataclass(frozen=True)
class AnalyzeWebpageResponse:
    page_id: str
    url: str


class AnalyzeWebpageUseCase:
    def __init__(
            self,
            notion_api: NotionApi,
            youtube_repository: YoutubeRepository | None = None,
            logger: logging.Logger | None = None) -> None:
        self.notion_api = notion_api
        self.youtube_repository = youtube_repository or NotionYoutubeRepository()
        self.logger = logger or logging.getLogger(__name__)


    def handle(self, original_url: str, attachment: dict) -> AnalyzeWebpageResponse | None:
        """指定されたWebページを分析して適宜保存する"""
        match SiteType.from_url(original_url):
            case SiteType.TWITTER:
                self.sub_handle_twitter(attachment=attachment)
            case SiteType.YOUTUBE:
                youtube = self.youtube_repository.save_from_attachment(url=original_url, attachment=attachment)
                return AnalyzeWebpageResponse(
                    page_id=youtube.notion_page_id,
                    url=youtube.notion_page_url,
                )
            case SiteType.WRESTLE_UNIVERSE:
                self.sub_handle_wrestle_universe(attachment=attachment)
            case SiteType.DEFAULT:
                self.sub_handle_default(attachment=attachment)

        # except Exception:
        #     import sys
        #     import traceback
        #     exc_info = sys.exc_info()
        #     t, v, tb = exc_info
        #     formatted_exception = "\n".join(
        #         traceback.format_exception(t, v, tb))
        #     text=f"analyze_inbox: error ```{formatted_exception}```"
        #     self.client.chat_postMessage(text=text, channel=channel, thread_ts=thread_ts)

    def sub_handle_default(self, attachment: dict) -> None:
        title = attachment["title"]
        original_url = attachment["original_url"]
        cover = attachment.get("image_url")
        self.notion_api.create_webclip_page(
            url=original_url,
            title=title,
            cover=cover,
        )

    def sub_handle_twitter(self, attachment: dict) -> str:
        """ 指定したURLのページをスクレイピングしてテキストを返す(X版) """
        text = attachment["text"]
        original_url = attachment["original_url"]
        cover = attachment.get("image_url") or attachment.get("thumb_url")
        self._create_webclip_page(url=original_url, title=text, cover=cover)

    def _create_webclip_page(self, url: str, title: str, cover: str) -> dict:
        return self.notion_api.create_webclip_page(
            url=url,
            title=title,
            cover=cover,
        )

    def sub_handle_youtube(self, attachment: dict) -> None:
        """ 指定したURLの動画を登録する """
        title = attachment["title"] + " | " + attachment["author_name"]
        original_url = attachment["original_url"]
        cover = attachment.get("thumb_url")
        author_name = attachment.get("author_name")
        # FIXME: author_nameを追加して、後続の処理も実装する
        self._create_video_page(url=original_url,
                                 title=title,
                                 cover=cover,
                                 tags=[])

    def _create_video_page(self, url: str, title: str, cover: str, tags: list[str]) -> dict:
        return self.notion_api.create_video_page(
            url=url,
            title=title,
            cover=cover,
            tags=tags,
        )

    def sub_handle_wrestle_universe(self, attachment: dict) -> str:
        """ 指定したURLの動画を登録する """
        def get_promotion_name(group_key: str) -> str:
            match group_key:
                case "tjpw":
                    return "東京女子プロレス"
                case _:
                    return group_key

        original_url:str = attachment["original_url"]
        event_id = original_url.split("/")[-1]
        # event_url = f"https://api.wrestle-universe.com/v1/events/{event_id}?al=ja"
        api_url = f"https://api.wrestle-universe.com/v1/videoEpisodes/{event_id}?al=ja"
        response = requests.get(api_url)
        data:dict = response.json()
        self.logger.debug(json.dumps(data, ensure_ascii=False))
        title = data["displayName"]
        description = data["description"]
        date = Date.fromisoformat(data["labels"]["matchDate"].split("T")[0])
        cover = data["keyVisualUrl"]
        promotion_name = get_promotion_name(data["labels"]["group"])
        tags = [promotion_name]
        if "venue" in data["labels"]:
            tags.append(data["labels"]["venue"])

        self._create_prowrestling_page(
            url=original_url,
            title=title,
            date=date,
            promotion=promotion_name,
            text=description,
            tags=tags,
            cover=cover,
        )

    def _create_prowrestling_page(self, url: str, title: str, date: Date, promotion: str, text: str, tags: list[str], cover: str) -> dict:
        print(title, date, promotion, text, tags, cover)
        return self.notion_api.create_prowrestling_page(
            url=url,
            title=title,
            date=date,
            promotion=promotion,
            text=text,
            tags=tags,
            cover=cover,
        )




if __name__ == "__main__":
    # python -m usecase.analyze_inbox
    import os

    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    logging.basicConfig(level=logging.DEBUG)
    usecase = AnalyzeInbox(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        notion_api=LambdaNotionApi(),
        logger=logging.getLogger(__name__),
    )
    attachment = {
        "original_url": "https://www.wrestle-universe.com/ja/lives/a6LxWJxRVkMM8TqZanndgh",
    }
    usecase.handle(attachment, "C05H3USHAJU", "1706271210.390809")
