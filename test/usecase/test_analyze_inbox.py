import datetime
import logging
import unittest
from unittest.mock import Mock, patch

from slack.infrastructure.api.lambda_notion_api import LambdaNotionApi
from slack.usecase.analyze_inbox import AnalyzeInbox
from slack_sdk.web import WebClient

DUMMY_CHANNEL = "C05H3USHAJU"
DUMMY_THREAD_TS = "1707452514.914669"

class TestAnalyzeInbox(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        self.analyze_inbox = AnalyzeInbox(
            client=Mock(WebClient),
            notion_api=Mock(LambdaNotionApi),
            logger=logging.getLogger(__name__),
        )

    @patch("slack.usecase.analyze_inbox.AnalyzeInbox._create_video_page")
    def test_handle_youtube(self, mock_create_video_page: Mock) -> None:
        # mock
        mock_create_video_page.return_value = {
            "id": "mock_page_id",
            "url": "https://example.com",
        }
        self.analyze_inbox._create_video_page = mock_create_video_page

        # Given
        attachment = {
          "from_url": "https://www.youtube.com/watch?v=TPJkNq88wBM",
          "thumb_url": "https://i.ytimg.com/vi/TPJkNq88wBM/hqdefault.jpg",
          "thumb_width": 480,
          "thumb_height": 360,
          "video_html": '<iframe width="400" height="225" src="https://www.youtube.com/embed/TPJkNq88wBM?feature=oembed&autoplay=1&iv_load_policy=3" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen title="今年最後の質問コーナーだ！！みんな！観て‼︎!"></iframe>',
          "video_html_width": 400,
          "video_html_height": 225,
          "service_icon": "https://a.slack-edge.com/80588/img/unfurl_icons/youtube.png",
          "id": 1,
          "original_url": "https://www.youtube.com/watch?v=TPJkNq88wBM",
          "fallback": "YouTube Video: 今年最後の質問コーナーだ！！みんな！観て‼︎!",
          "title": "今年最後の質問コーナーだ！！みんな！観て‼︎!",
          "title_link": "https://www.youtube.com/watch?v=TPJkNq88wBM",
          "author_name": "ヘアピンまみれ Hairpin Mamire",
          "author_link": "https://www.youtube.com/@hairpin_mamire",
          "service_name": "YouTube",
          "service_url": "https://www.youtube.com/",
        }
        channel = "C05H3USHAJU"
        thread_ts = "1707452514.914669"

        # When
        _ = self.analyze_inbox.handle(attachment, channel, thread_ts)

        # Then
        mock_create_video_page.assert_called_once_with(
            url=attachment["original_url"],
            title=attachment["title"] + " | " + attachment["author_name"],
            cover=attachment["thumb_url"],
            tags=[],
        )

    @patch("slack.usecase.analyze_inbox.AnalyzeInbox._create_webclip_page")
    def test_handle_twitter(self, mock_create_webclip_page: Mock) -> None:
        # mock
        mock_create_webclip_page.return_value = {
            "id": "mock_page_id",
            "url": "https://example.com",
        }
        self.analyze_inbox._create_webclip_page = mock_create_webclip_page

        # Given
        attachment = {
            "from_url": "https://x.com/Toga_tjpw/status/1760269284264362358?s=20",
            "image_url": "https://pbs.twimg.com/media/GG27lLda8AAbcRm.jpg:large",
            "image_width": 2048,
            "image_height": 1536,
            "image_bytes": 359959,
            "service_icon": "http://abs.twimg.com/favicons/twitter.3.ico",
            "id": 1,
            "original_url": "https://x.com/Toga_tjpw/status/1760269284264362358?s=20",
            "fallback": "X (formerly Twitter): 凍雅 (@Toga_tjpw) on X",
            "text": "制服ポートレート発売開始しました！！\n\n撮影のときのオフショットと実際のJK時代の写真載せとくね:rolling_on_the_floor_laughing:\n\nみんないっぱいGETしてねっ:heart_hands::skin-tone-2::two_hearts:",
            "title": "凍雅 (@Toga_tjpw) on X",
            "title_link": "https://x.com/Toga_tjpw/status/1760269284264362358?s=20",
            "service_name": "X (formerly Twitter)",
        }
        channel = "C05H3USHAJU"
        thread_ts = "1707452514.914669"

        # When
        _ = self.analyze_inbox.handle(attachment, channel, thread_ts)

        # Then
        mock_create_webclip_page.assert_called_once_with(
            url=attachment["original_url"],
            title=attachment["text"],
            cover=attachment["image_url"],
        )

    @patch("slack.usecase.analyze_inbox.AnalyzeInbox._create_prowrestling_page")
    def test_handle_wrestle_universe(self, mock_create_prowrestling_page: Mock) -> None:
        # mock
        mock_create_prowrestling_page.return_value = {
            "id": "mock_page_id",
            "url": "https://example.com",
        }
        self.analyze_inbox._create_prowrestling_page = mock_create_prowrestling_page

        # Given
        attachment = {
            "original_url": "https://www.wrestle-universe.com/videos/rJmATVm3TxZTrsG2cbBjEz",
        }

        # When
        _ = self.analyze_inbox.handle(attachment, DUMMY_CHANNEL, DUMMY_THREAD_TS)

        # Then
        mock_create_prowrestling_page.assert_called_once_with(
            url=attachment["original_url"],
            title="ジンギスカン霧島 presents 紅白勝ち抜き戦",
            date=datetime.date(2020, 4, 3),
            promotion="東京女子プロレス",
            text="2020年4月3日  東京女子プロレス「ジンギスカン霧島 presents 紅白勝ち抜き戦」を配信！\n\n※権利上の都合により一部で消音する場合がございます。予めご了承ください。\n\n＜出場選手＞\n辰巳リカ、渡辺未詩、中島翔子、山下実優、ハイパーミサヲ、天満のどか、愛野ユキ、原宿ぽむ、桐生真弥、猫はるな、舞海魅星、鈴芽、汐凛セナ、伊藤麻希、まなせゆうな、瑞希、上福ゆき、乃蒼ヒカリ、らく、白川未奈\n※リングアナウンサー…難波小百合",
            tags=["東京女子プロレス"],
            cover="https://image.asset.wrestle-universe.com/if8s93gLo7LaL3JYqLP4nR/if8s93gLo7LaL3JYqLP4nR",
        )
