import logging
from dataclasses import dataclass
from enum import IntEnum

from domain.channel.thread import Thread
from domain.puroresu.puroresu import NotionProRepository, Puroresu, PuroresuRepository
from domain.webclip.webclip import NotionWebclipRepository, WebclipRepository
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
            youtube_repository: YoutubeRepository | None = None,
            webclip_repository: WebclipRepository | None = None,
            pubroresu_repository: PuroresuRepository | None = None,
            logger: logging.Logger | None = None) -> None:
        self.youtube_repository = youtube_repository or NotionYoutubeRepository()
        self.webclip_repository = webclip_repository or NotionWebclipRepository()
        self.puroresu_repository = pubroresu_repository or NotionProRepository()
        self.logger = logger or logging.getLogger(__name__)


    def handle(self, original_url: str, attachment: dict, slack_thread: Thread|None = None) -> AnalyzeWebpageResponse:
        """指定されたWebページを分析して適宜保存する"""
        # FIXME: SiteTypeというか、Webpageの種類とカテゴリを持つモデルをつくるか
        match SiteType.from_url(original_url):
            case SiteType.TWITTER:
                attachment_for_twitter = {
                    "title": attachment["text"],
                    "thumb_url": attachment.get("thumb_url"),
                    "image_url": attachment.get("image_url"),
                }
                webclip = self.webclip_repository.save_from_attachment(url=original_url, attachment=attachment_for_twitter, thread=slack_thread)
                return AnalyzeWebpageResponse(
                    page_id=webclip.notion_page_id,
                    url=webclip.notion_page_url,
                )
            case SiteType.YOUTUBE:
                youtube = self.youtube_repository.save_from_attachment(url=original_url, attachment=attachment)
                return AnalyzeWebpageResponse(
                    page_id=youtube.notion_page_id,
                    url=youtube.notion_page_url,
                )
            case SiteType.WRESTLE_UNIVERSE:
                puroresu = Puroresu.create_from_wrestle_universe(url=original_url)
                puroresu = self.puroresu_repository.save(puroresu)
                return AnalyzeWebpageResponse(
                    page_id=puroresu.notion_page_id,
                    url=puroresu.notion_page_url,
                )
            case SiteType.DEFAULT:
                webclip = self.webclip_repository.save_from_attachment(url=original_url, attachment=attachment, thread=slack_thread)
                return AnalyzeWebpageResponse(
                    page_id=webclip.notion_page_id,
                    url=webclip.notion_page_url,
                )
