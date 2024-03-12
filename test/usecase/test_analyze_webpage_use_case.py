import logging
import unittest
from unittest.mock import Mock

from slack.domain.channel.thread import Thread
from slack.domain.puroresu.puroresu import PuroresuRepository
from slack.domain.webclip.webclip import WebclipRepository
from slack.domain.youtube.youtube import YoutubeRepository
from slack.usecase.analyze_webpage_use_case import AnalyzeWebpageUseCase

DUMMY_SLACK_THREAD = Thread(
    channel_id="mock_channel_id",
    thread_ts="mock_thread_ts",
    event_ts="mock_event_ts",
)

class TestAnalyzeWebpageUseCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        youtube_repository = Mock(YoutubeRepository)
        webclip_repository = Mock(WebclipRepository)
        puroresu_repository = Mock(PuroresuRepository)
        self.suite = AnalyzeWebpageUseCase(
            youtube_repository=youtube_repository,
            webclip_repository=webclip_repository,
            pubroresu_repository=puroresu_repository,
            logger=logging.getLogger(__name__),
        )

    def test_通常のWebClip(self) -> None:

        # Given
        attachment = {
            "original_url": "https://example.com",
            "image_url": "https://example.com/hoge.jpg",
            "title": "テスト",
        }

        self.suite.handle(original_url=attachment["original_url"], attachment=attachment, slack_thread=DUMMY_SLACK_THREAD)

        # Then
        self.suite.webclip_repository.save_from_attachment.assert_called_once_with(
            url=attachment["original_url"], attachment=attachment, slack_thread=DUMMY_SLACK_THREAD
        )

    def test_handle_youtube(self) -> None:
        # Given
        title = "今年最後の質問コーナーだ！！みんな！観て‼︎!"
        original_url = "https://www.youtube.com/watch?v=TPJkNq88wBM"
        thumb_url = "https://i.ytimg.com/vi/TPJkNq88wBM/hqdefault.jpg"
        author_name = "ヘアピンまみれ Hairpin Mamire"
        attachment = {
          "title": title,
          "thumb_url": thumb_url,
          "original_url": original_url,
          "author_name": author_name,
        #   "video_html": '<iframe width="400" height="225" src="https://www.youtube.com/embed/TPJkNq88wBM?feature=oembed&autoplay=1&iv_load_policy=3" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen title="今年最後の質問コーナーだ！！みんな！観て‼︎!"></iframe>',
        #   "from_url": "https://www.youtube.com/watch?v=TPJkNq88wBM",
        #   "thumb_width": 480,
        #   "thumb_height": 360,
        #   "video_html_width": 400,
        #   "video_html_height": 225,
        #   "id": 1,
        #   "service_icon": "https://a.slack-edge.com/80588/img/unfurl_icons/youtube.png",
        #   "fallback": "YouTube Video: 今年最後の質問コーナーだ！！みんな！観て‼︎!",
        #   "title_link": "https://www.youtube.com/watch?v=TPJkNq88wBM",
        #   "author_link": "https://www.youtube.com/@hairpin_mamire",
        #   "service_name": "YouTube",
        #   "service_url": "https://www.youtube.com/",
        }

        # When
        self.suite.handle(original_url=attachment["original_url"], attachment=attachment)

        # Then
        self.suite.youtube_repository.save_from_attachment.assert_called_once_with(
            url=original_url, attachment=attachment, slack_thread=None)

    def test_handle_twitter(self) -> None:

        # Given
        attachment = {
            "original_url": "https://x.com/Toga_tjpw/status/1760269284264362358?s=20",
            "image_url": "https://pbs.twimg.com/media/GG27lLda8AAbcRm.jpg:large",
            "text": "制服ポートレート発売開始しました！！\n\n撮影のときのオフショットと実際のJK時代の写真載せとくね:rolling_on_the_floor_laughing:\n\nみんないっぱいGETしてねっ:heart_hands::skin-tone-2::two_hearts:",
            "title": "凍雅 (@Toga_tjpw) on X",
            # "from_url": "https://x.com/Toga_tjpw/status/1760269284264362358?s=20",
            # "image_width": 2048,
            # "image_height": 1536,
            # "image_bytes": 359959,
            # "service_icon": "http://abs.twimg.com/favicons/twitter.3.ico",
            # "id": 1,
            # "fallback": "X (formerly Twitter): 凍雅 (@Toga_tjpw) on X",
            # "title_link": "https://x.com/Toga_tjpw/status/1760269284264362358?s=20",
            # "service_name": "X (formerly Twitter)",
        }

        # When
        self.suite.handle(original_url=attachment["original_url"], attachment=attachment)

        # Then
        expected_attachment = {
            "title": attachment["text"],
            "thumb_url": None,
            "image_url": attachment["image_url"],
        }
        self.suite.webclip_repository.save_from_attachment.assert_called_once_with(
            url=attachment["original_url"], attachment=expected_attachment, slack_thread=None
        )

    def test_handle_wrestle_universe(self) -> None:
        # Given
        attachment = {
            "original_url": "https://www.wrestle-universe.com/videos/rJmATVm3TxZTrsG2cbBjEz",
        }

        # When
        self.suite.handle(original_url=attachment["original_url"], attachment=attachment)

        # Then
        self.suite.puroresu_repository.save.assert_called_once()
