import logging
from dataclasses import dataclass
from enum import IntEnum

from domain.channel.thread import Thread
from domain.puroresu.puroresu import NotionProRepository, Puroresu, PuroresuRepository
from domain.webclip.webclip import NotionWebclipRepository, WebclipRepository
from domain.youtube.youtube import NotionYoutubeRepository, YoutubeRepository
from util.slack_client_wrapper import SlackClientWrapper, SlackClientWrapperMock


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
            slack_client_wrapper: SlackClientWrapper | None = None,
            logger: logging.Logger | None = None,
            ) -> None:
        self.youtube_repository = youtube_repository or NotionYoutubeRepository()
        self.webclip_repository = webclip_repository or NotionWebclipRepository()
        self.puroresu_repository = pubroresu_repository or NotionProRepository()
        self.logger = logger or logging.getLogger(__name__)
        self.slack_client_wrapper = slack_client_wrapper or SlackClientWrapperMock()


    def handle(self, original_url: str, attachment: dict, slack_thread: Thread = None) -> None:
        """指定されたWebページを分析する。分析は非同期で行われるため依頼のみする"""
        if slack_thread:
            if self.slack_client_wrapper.is_reacted(
                name="white_check_mark",
                channel=slack_thread.channel_id,
                timestamp=slack_thread.thread_ts):
                print("既にリアクションがついているので処理をスキップします。")
                return
            self.slack_client_wrapper.reactions_add(
                name="white_check_mark",
                channel=slack_thread.channel_id,
                timestamp=slack_thread.thread_ts)
        match SiteType.from_url(original_url):
            # FIXME: SiteTypeというか、Webpageの種類とカテゴリを持つモデルをつくるか
            case SiteType.TWITTER:
                attachment_for_twitter = {
                    "title": attachment["text"],
                    "thumb_url": attachment.get("thumb_url"),
                    "image_url": attachment.get("image_url"),
                }
                self.webclip_repository.save_from_attachment(url=original_url, attachment=attachment_for_twitter, slack_thread=slack_thread)
            case SiteType.YOUTUBE:
                self.youtube_repository.save_from_attachment(url=original_url, attachment=attachment, slack_thread=slack_thread)
            case SiteType.WRESTLE_UNIVERSE:
                puroresu = Puroresu.create_from_wrestle_universe(url=original_url)
                self.puroresu_repository.save(puroresu)
            case SiteType.DEFAULT:
                self.webclip_repository.save_from_attachment(url=original_url, attachment=attachment, slack_thread=slack_thread)
